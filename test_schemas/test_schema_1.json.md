
#*test\_schema\_1.json* schema documentation
#####Generated by [doctor\_jsonschema\_md](https://github.com/rdpickard/doctor_jsonschema_md)
---
#####Source file: ```test_schemas/test_schema_1.json```
#####Documentations generation date: 2016-01-10 20:39
---
####Title: None
####Description: schema for an fstab entry
####Schema: http://json-schema.org/draft-04/schema#
####ID: http://some.site.somewhere/entry-schema#
####Properties Index:
* [readonly](#readonly)
* [storage](#storage)
* [options](#options)
* [fstype](#fstype)

####References Index:
* [tmpfs](#tmpfs)
* [diskDevice](#diskdevice)
* [nfs](#nfs)
* [diskUUID](#diskuuid)


####Properties Detail:
+ 

	+ <a id="readonly"></a> **readonly**
		+ _Type:_ boolean
		+ _Required:_ False
		+ _Description:_ None
		+ _Allowed values:_ Any


	+ <a id="storage"></a> **storage**
		+ _Type:_ object
		+ _Required:_ True
		+ _Description:_ None
		+ _Allowed values:_ Any
		+ _Children_:



	+ <a id="options"></a> **options**
		+ _Type:_ array
		+ _Required:_ False
		+ _Description:_ None
		+ _Allowed values:_ Any
		+ _Unique Items:_ True
		+ _Minimum Items:_ 1
		+ _Maximum Items:_ NA
		+ <a id="items"></a> **items**
			+ _Type:_ string
			+ _Required:_ False
			+ _Description:_ None
			+ _Allowed values:_ Any



	+ <a id="fstype"></a> **fstype**
		+ _Required:_ False
		+ _Description:_ None
		+ _Allowed values:_ ```ext3```,```ext4```,```btrfs```





####Object References
+ <a id="tmpfs"></a> **tmpfs**
	+ _Required:_ False
	+ _Description:_ None
	+ _Allowed values:_ Any

+ <a id="diskdevice"></a> **diskDevice**
	+ _Required:_ False
	+ _Description:_ None
	+ _Allowed values:_ Any

+ <a id="nfs"></a> **nfs**
	+ _Required:_ False
	+ _Description:_ None
	+ _Allowed values:_ Any

+ <a id="diskuuid"></a> **diskUUID**
	+ _Required:_ False
	+ _Description:_ None
	+ _Allowed values:_ Any


    