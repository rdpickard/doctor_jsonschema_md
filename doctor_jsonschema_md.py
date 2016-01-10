import json
import os
import logging
import time
import re

_mds = lambda s: s.replace("_", "\_")

def _addref(referencepath, markdowndictionary, fulljson):

    if re.match("^#/(.*)", referencepath):
        g = re.match("^#/(.*)", referencepath).groups()
        paths = g[0].split("/")
        cjson = fulljson
        for path in paths:
            cjson = cjson[path]

        rmd = _jelem2md(cjson,
                        g[0],
                        cjson["type"],
                        markdowndictionary,
                        fulljson)

        rmd += "+ _Childelements_\n"
        for propertykey in cjson["properties"].keys():
            rmd += "\n"

            rmd += _jelem2md(cjson["properties"][propertykey],
                      "**"+propertykey+"**",
                      cjson["properties"][propertykey]["type"],
                      markdowndictionary,
                      fulljson,
                      indent="\t",
                      header="+ ")

        markdowndictionary["references"][g[0]] = rmd

    pass

def _jref2md(jsonelement, name, required=False):
    md = "######"
    if required:
        md += "_{}_ (reference) required \n".format(_mds(name))
    else:
        md += "_{}_ (reference) optional \n".format(_mds(name))
    if "$ref"  in jsonelement.keys():
        md = "+ _Reference:_ {}\n".format(jsonelement.get("$ref","None"))

    return md

def _jelem2md(jsonelement, name, etype, markdowndict, fulljson, required=False, indent="", header="######"):

    md = "{}{} {}\n".format(indent, header, _mds(name))

    indent=indent+indent
    if type(etype) == list and type(etype) != str:
        md += "{}+ _Types_:  \n".format(indent)
        for et in etype:
            if type(et) == str:
                md += "{}     + {}\n".format(indent, et)
            elif type(et) == dict and "$ref" in et.keys():
                md += "{}     + {}\n".format(indent, et["$ref"])
                _addref(et["$ref"], markdowndict, fulljson)
    else:
        md += "{}+ _Type_: {}  \n".format(indent, etype)

    md += "{}+ _Required_: {} \n".format(indent, "*True*" and required or "False")

    if "$ref"  in jsonelement.keys():
        md += "{}+ _Reference:_ {}\n".format(indent, jsonelement.get("$ref","None"))

    md += "{}+ _Description:_ {}\n".format(indent, _mds(jsonelement.get("description","None")))

    if "enum" in jsonelement.keys():
        md += "{}+ _Allowed values:_ {}\n".format(indent, ",".join(map(lambda o: "```"+o+"```", jsonelement["enum"])))
    else:
        md += "{}+ _Allowed values:_ Any\n".format(indent)

    if "default" in jsonelement.keys():
        md += "{}+ _Default_ ```{}```\n".format(indent, jsonelement["default"])

    return md


def _j2m(jsonelement, jsonelementpath, markdowndict, fulljson, example_files=list(), logger=logging.getLogger()):

    if jsonelement.get("type", "derp").lower() == "object":

        if jsonelementpath == "":
            p = "[ROOT]"
        else:
            p = jsonelementpath
        omd = _jelem2md(jsonelement, p, jsonelement["type"], markdowndict, fulljson)
        omd += "+ _Childelements_\n"

        for propertykey in jsonelement["properties"].keys():
            if jsonelementpath == "":
                propname=propertykey
            else:
                propname=jsonelementpath+"."+propertykey
            omd += "     + [{}](#{})\n".format(_mds(propertykey), propname)
            omd += "\n"

            _j2m(jsonelement["properties"][propertykey], propname, markdowndict, fulljson)
        if jsonelementpath != "":
            markdowndict["elements"][jsonelementpath] = omd

    elif "$ref" in jsonelement.keys():
        markdowndict["elements"][jsonelementpath] = _jref2md(jsonelement, jsonelementpath)
    elif jsonelement.get("type", "derp").lower() in ["string", "array", "boolean", "number"]:
        markdowndict["elements"][jsonelementpath] = _jelem2md(jsonelement,
                                                              jsonelementpath,
                                                              jsonelement["type"],
                                                              markdowndict,
                                                              fulljson)
    elif jsonelement.get("oneOf", None) is not None:
        markdowndict["elements"][jsonelementpath] = _jelem2md(jsonelement,
                                                              jsonelementpath,
                                                              jsonelement["oneOf"],
                                                              markdowndict,
                                                              fulljson)

    else:
        raise ValueError("Unknown JSON Schema type <%s>" % jsonelement["type"])

def jsonschema_to_markdown(schema_filepath, markdown_outputfile=None, example_files=list(), logger=logging.getLogger()):
    """
    Creates a Markdown representation of a JSON schema.

    :param schema_filepath: Path to the schema to generate MD from
    :param markdown_outputfile: (optional A file to write the generated MD to
    :param example_files: (optional) A list of paths to files of JSON that implement the specfiied schema
    :param logger: (optional) where to log messages to. defaults to basic logger
    :return: generated markdown as a string
    """

    if not os.path.isfile(schema_filepath):
        logger.error("File [{}] does not seem to exist".format(schema_filepath))
        raise ValueError("No such file %s" % schema_filepath)

    schema_file = open(schema_filepath, "r")
    try:
        schema = json.load(schema_file)
    except ValueError as ve:
        msg = "File [{}] does not seem to be JSON".format(schema_filepath)
        logger.error(msg)
        raise ve


    if schema.get("type","derp").lower() != 'object':
        raise ValueError("File [{}] does not seem to be JSON a json schema".format(schema_filepath))
    if schema.get("$schema", "derp") !=  "http://json-schema.org/draft-04/schema#":
        raise ValueError("File [{}] is not a supported schema version <{}>".format(schema_filepath,
                                                                                   schema.get("$schema", "(no schema)")
                                                                                   )
                         )
    mddict = dict()
    mddict["title"] = schema.get("title","No Title")
    mddict["elements"] = dict()
    mddict["references"] = dict()

    _j2m(jsonelement=schema, jsonelementpath="", markdowndict=mddict, fulljson=schema, example_files=example_files)

    md = """
#*{}* schema documentation
Generated from file ```{}``` on {} by [doctor\_jsonschema\_md](https://github.com/rdpickard/doctor_jsonschema_md)

##Elements
{}

##References
{}
    """.format(_mds(schema_filepath.split("/")[-1]),
               schema_filepath,
               time.strftime("%Y-%m-%d %H:%M"),
               "\n".join(map( lambda e: mddict["elements"][e], sorted(mddict["elements"]))),
               "\n".join(map( lambda e: mddict["references"][e], sorted(mddict["references"]))))

    return md

if __name__ == "__main__":
  md = jsonschema_to_markdown("/Users/pickard/projects/LinkNYC/register.citybridge.com/schemas/aws_bootstrap.configschema.json")
  print md