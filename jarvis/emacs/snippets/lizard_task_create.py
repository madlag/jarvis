import lizard.task.base

class {{ClassName}}Task(lizard.task.base.LizardTask):
    directory = {"input":[{"name":"url", "type":"url:mime:video/*", "required":False},
                          {"name":"width", "type":"int", "required":False},
                          ],
                 "files":[{"name":"out.mp4", "type":"mime:video/mp4", "required":False},
                          ], 
                 "meta" :[
                          {"name":"quality", "type":"int"},
                          {"name":"content-type", "type":"str:video/mp4"}
                          ],
                 "checkInterval":240,
                 }    


    def run(self, url, width):
        filename = self.download(url, "input")
        filename = "TODO"
        mimeType = "TODO"
        self.store("out.mp4", filename = filename, mimeType = mimeType)

        meta = {}
        meta["content-type"] = mimeType
        meta["quality"] = 2

        return meta


        
