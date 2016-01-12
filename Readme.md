#Doctor JSONschema, M.D. 

A utility script to generate documentation in [Markdown](https://daringfireball.net/projects/markdown/syntax) format 
from [JSON schema](http://json-schema.org/) files. 

![ss](docs/media/transform.png)

Well written JSONschemas contain a lot of contextual information about the document they are intended to validate. 
Being able to generate documentation from them automagically from schemas reduces the repetative work of craft 
long stretches of Markdown by hand and reduces the chance of drift between documentation and implementation. 

While the utopia of JSON as a markup for all things [has not emerged](http://www.redbook.io/pdf/ch1-background.pdf) from
the rubble of it's predicesors, I belive it does have a lot of utility for describing small, self contained elements 
such as configuration files and data exchange for RESTful APIs.

The name is a reference to a joke between a [friend](https://github.com/timmattison) and I about developers calling 
themselves Engineers, for about a week he asked everyone to call him a Medical Doctor of Java. 

###Requirements
Python 2.7 must be installed.

The required Python support modules can be installed using pip

```
pip install -r requirements.txt
```

###Running
The ```doctor_jsonschema_md``` has three command line switches

+ _schemafile_ The file path to the schema to generate Markdown for
+ _outfile_ (optional) The file path for the generated Markdown file. If it outfile is not specified, the generated 
Markdown data will be send to stdout
+ _overwrite_ (optional) Setting this switch will overwrite the file specified by _outfile_ if it exists

###Examples

+ Generate MD for file ```test_schemas/test_schema_1.json``` and out put to terminal 

	```
	python doctor_jsonschema_md.py --schema test_schemas/test_schema_1.json
	```

+ Generate MD for file ```test_schemas/test_schema_1.json``` and out put to file  
```test_schemas/test_schema_1.json.md ```

	```
	python doctor_jsonschema_md.py --schema test_schemas/test_schema_1.json \
	--outfile test_schemas/test_schema_1.json.md -
	```
	
###Example Output

+ From screen shot above [JSON schema](test_schemas/test_schema_1.json) / [Markdown](test_schemas/test_schema_1.json.md)

+ From another project [JSON schema](test_schemas/test_schema_2.json) / [Markdown](test_schemas/test_schema_2.json.md)

###TODOs

+ The entire JSONschema standard is not implemented. Need to support the entire language set

+ Be able to generate example data from input of JSON documents. 