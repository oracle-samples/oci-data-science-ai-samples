# Important

If you want to make a ZIP file to upload to run as a Job on your Mac Computer, you should better use following:

```bash
zip -r zip-runtime-yaml-artifact.zip zip-runtime-yaml-artifact/ -x ".*" -x "__MACOSX"
```
