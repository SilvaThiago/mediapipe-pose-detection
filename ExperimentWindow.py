class ExperimentWindow:
    def __init__(self, chosenCamera=None, cameraIndex=None, resultFilePath=None, showPreview=True, saveVideo=True, textureWidth=1280, textureHeight=720):
        self.chosenCamera = chosenCamera
        self.cameraIndex = cameraIndex
        self.resultFilePath = resultFilePath
        self.showPreview = showPreview
        self.saveVideo = saveVideo
        self.textureWidth = textureWidth
        self.textureHeight = textureHeight