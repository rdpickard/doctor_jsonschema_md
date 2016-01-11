import json
import os
import logging
import time
import sys
import argparse

def _mds(s, iscode=False):
    # P Is this json?

    if iscode and type(s) == dict:
        try:
            js = json.dumps(s, sort_keys=True, indent=4, separators=(',', ': '))
            return js
        except:
            return s
            pass
    elif iscode:
        return s
    else:
        ms = s.replace("_", "\_")

    return ms

def _json2markdown(jsonelement, elementname, jsonparent, parentpath, indenttabs=0):
    """

    :param jsonelement:
    :param jsonparent:
    :param indenttabs:
    :param markdowndict:
    :return:
    """
    md = ""
    elementtype = jsonelement.get("type", "")

    if elementtype == "" and "$ref" in jsonelement.keys():
        elementtype = "[{}](#{})".format(jsonelement.get("$ref"), jsonelement.get("$ref").split("/")[-1])

    indent = "".join(["\t"] * indenttabs)

    if elementname is not None and elementname != "":

        if parentpath is None:
            md += "{}+ <a id=\"{}\"></a> **{}**\n".format(indent, elementname.lower(), _mds(elementname))
        else:
            md += "{}+ <a id=\"{}.{}\"></a> **{}**\n".format(indent, parentpath.lower(), elementname.lower(),
                                                           _mds(elementname))

        if elementtype != "" and (type(elementtype) == str or type(elementtype) == unicode):
            md += "{}\t+ _Type:_ {}\n".format(indent, _mds(elementtype))
        elif elementtype != "" and type(elementtype) == list:
            md += "{}\t+ _Types:_ {}\n".format(indent, ",".join(map(lambda t: _mds(t), elementtype)))
        elif jsonelement.get("oneOf", None) is not None:
            md += "{}\t+ _Type one of:_ {}\n".format(indent, _mds(elementtype))

            for et in jsonelement["oneOf"]:
                if type(et) == str:
                    md += "{}\t\t+ {}\n".format(indent, et)
                elif type(et) == dict and "$ref" in et.keys():
                    md += "{}\t\t+ [{}](#{})\n".format(indent, et["$ref"], et["$ref"].split("/")[-1])

        if jsonparent is not None and "required" in jsonparent.keys() and elementname in jsonparent["required"]:
            md += "{}\t+ _Required:_ True\n".format(indent)
        else:
            md += "{}\t+ _Required:_ False\n".format(indent)

        md += "{}\t+ _Description:_ {}\n".format(indent, jsonelement.get("description", "None"))

        if "enum" in jsonelement.keys():
            md += "{}\t+ _Allowed values:_ {}\n".format(indent,
                                                      ",".join(map(lambda o: "```" + o + "```", jsonelement["enum"])))
        else:
            md += "{}\t+ _Allowed values:_ Any\n".format(indent)

        if "default" in jsonelement.keys():
            d = _mds(jsonelement["default"], True)
            md += "{}\t+ _Default:_ ```{}```\n".format(indent, d)

    if elementtype == "object":
        if elementname is not None and elementname != "":
            md += "{}\t+ _Children_:\n\n".format(indent)
        else:
            md += "{}+ \n\n".format(indent)

        if parentpath is not None and parentpath != "":
            path = parentpath + "." + elementname
        elif elementname is not None:
            path = elementname
        else:
            path = None

        for property in jsonelement.get("properties",{}).keys():
            md += _json2markdown(jsonelement["properties"][property], property, jsonelement, path, indenttabs + 1)
            md += "\n"

    elif elementtype in ["string",  "boolean", "number"]:
        pass
    elif elementtype == "array":
        md += "{}\t+ _Unique Items:_ {}\n".format(indent, jsonelement.get("uniqueItems", "False"))
        md += "{}\t+ _Minimum Items:_ {}\n".format(indent, jsonelement.get("minItems", "NA"))
        md += "{}\t+ _Maximum Items:_ {}\n".format(indent, jsonelement.get("maxItems", "NA"))
        if "items" in jsonelement.keys():
            md += _json2markdown(jsonelement["items"], "items", jsonelement, parentpath, indenttabs+1)
    else:
        # raise ValueError("Unknown JSON Schema type <%s>" % jsonelement["type"])
        pass

    md += "\n"
    return md


def _json_index_markdown(jsonelement, parentelement, elementname):
    md = ""

    if elementname is not None and elementname != "":
        md += "* [{}](#{})\n".format(_mds(elementname), elementname.lower())

    if type(jsonelement) != dict:
        pass
    elif "type" in jsonelement.keys() and jsonelement["type"] == "object" and "properties" in jsonelement.keys():
        for prop in jsonelement["properties"]:

            if elementname is not None and elementname != "":
                md += _json_index_markdown(jsonelement["properties"][prop], jsonelement, elementname + "." + prop)
            else:
                md += _json_index_markdown(jsonelement["properties"][prop], jsonelement, prop)
    elif False in map(lambda k: type(jsonelement[k]) == dict, jsonelement.keys()):
        pass
    elif type(jsonelement) == dict and "type" not in jsonelement.keys():
        for k in jsonelement.keys():
            md += _json_index_markdown(jsonelement[k], {}, k)

    return md


def jsonschema_to_markdown(schema_filepath,
                           markdown_outputfile=None,
                           overwrite_outputfile=False,
                           example_files=list(),
                           logger=logging.getLogger()):
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

    if schema.get("type", "derp").lower() != 'object':
        raise ValueError("File [{}] does not seem to be JSON a json schema".format(schema_filepath))
    if schema.get("$schema", "derp") != "http://json-schema.org/draft-04/schema#":
        raise ValueError("File [{}] is not a supported schema version <{}>".format(schema_filepath,
                                                                                   schema.get("$schema", "(no schema)")
                                                                                   )
                         )

    mdfile = None
    if markdown_outputfile is not None:
        if os.path.isfile(markdown_outputfile) and not overwrite_outputfile:
            logging.error("Markdown file [%s] exists. Remove or rerun script with --overwrite")
            return None
        elif os.path.isfile(markdown_outputfile):
            os.remove(markdown_outputfile)
        elif not os.path.isdir(os.sep.join(markdown_outputfile.split(os.sep)[:-1])):
            os.makedirs(os.sep.join(markdown_outputfile.split(os.sep)[:-1]))
        mdfile = open(markdown_outputfile, "w+")

    mddict = dict()
    mddict["title"] = schema.get("title", "No Title")
    mddict["elements"] = dict()
    mddict["references"] = dict()

    emd = _json2markdown(jsonelement=schema,
                         elementname=None,
                         jsonparent=None,
                         parentpath=None,
                         indenttabs=0)

    rmd = ""
    stds=["type", "id", "description", "title", "$schema", "properties", "required"]
    for skey in filter(lambda k: k not in stds and type(schema[k]) == dict, schema.keys()):
        for rkey in schema[skey].keys():
            rmd += _json2markdown(jsonelement=schema[skey][rkey],
                                 elementname=rkey,
                                 jsonparent=None,
                                 parentpath=None,
                                 indenttabs=0)


    md = """
#*{}* schema documentation
#####Generated by [doctor\_jsonschema\_md](https://github.com/rdpickard/doctor_jsonschema_md)
---
#####Source file: ```{}```
#####Documentations generation date: {}
---
####Title: {}
####Description: {}
####Schema: {}
####ID: {}
####Properties Index:
{}
####References Index:
{}

####Properties Detail:
{}

####Object References
{}
    """.format(_mds(schema_filepath.split("/")[-1]),
               schema_filepath,
               time.strftime("%Y-%m-%d %H:%M"),
               schema.get("title", "None"),
               schema.get("description", "_None_"),
               schema.get("$schema", "_None_"),
               schema.get("id", "_None_"),
               _json_index_markdown(schema, None, ""),
               _json_index_markdown(schema['definitions'], None, ""),
               emd,
               rmd)

    if mdfile is not None:
        mdfile.write(md)
        mdfile.close()

    return md


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Bootstrap script to deploy register.citybridge.com in AWS')

    parser.add_argument('--schemafile', type=str, required=True,
                        help='Path to schema file to use')

    parser.add_argument('--outfile', type=str, required=False, default=None,
                        help='Path markdown file')

    parser.add_argument('--overwrite', action='store_true', dest='overwrite', required=False,
                        default=False,
                        help='Overwrite markdown file if exists')

    args = parser.parse_args()
    md = jsonschema_to_markdown(args.schemafile, args.outfile, args.overwrite)
    if args.outfile is None:
        print md