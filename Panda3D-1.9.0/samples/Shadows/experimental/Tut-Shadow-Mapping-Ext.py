from pandac.PandaModules import *
import sys,os

#loadPrcFileData("", "fullscreen 1")
#loadPrcFileData('', 'show-buffers 1')
#loadPrcFileData("", "framebuffer-multisample 1")
#loadPrcFileData("", 'vfs-case-sensitive 0')

# loadPrcFileData('', 'want-pstats 1')
# os.spawnl(os.P_NOWAIT, "D:/Panda3D-1.3.2/bin/pstats.exe")
# PStatClient.connect()

import direct.directbase.DirectStart
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.actor import Actor
from random import *

# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1), mayChange=1,
                        pos=(-1.3, pos), align=TextNode.ALeft, scale = .05, shadow=(0,0,0,1), shadowOffset=(0.1,0.1))

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1,1,1,1),
                        pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)

class World(DirectObject):
    def __init__(self):
        # Preliminary capabilities check.
    
        if (base.win.getGsg().getSupportsBasicShaders()==0):
            self.t=addTitle("Shadow Demo: Video driver reports that shaders are not supported.")
            return
        if (base.win.getGsg().getSupportsDepthTexture()==0):
            self.t=addTitle("Shadow Demo: Video driver reports that depth textures are not supported.")
            return
          
        # creating the offscreen buffer.
    
        winprops = WindowProperties.size(512,512)
        props = FrameBufferProperties()
        props.setRgbColor(1)
        props.setAlphaBits(1)
        props.setDepthBits(1)
        LBuffer = base.graphicsEngine.makeOutput(
                 base.pipe, "offscreen buffer", -2,
                 props, winprops,
                 GraphicsPipe.BFCanBindEvery | GraphicsPipe.BFRttCumulative | GraphicsPipe.BFRefuseWindow,
                 base.win.getGsg(),base.win)
    
        if (LBuffer == None):
           self.t=addTitle("Shadow Demo: Video driver cannot create an offscreen buffer.")
           return
        
        Ldepthmap = Texture()
        LBuffer.addRenderTexture(Ldepthmap, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPDepth)
        Ldepthmap.setMinfilter(Texture.FTShadow) # to use OpenGL SGIX_shadow extension
        Ldepthmap.setMagfilter(Texture.FTShadow) 

	# Adding a color texture is totally unnecessary, but it helps with debugging.
        Lcolormap = Texture()
        LBuffer.addRenderTexture(Lcolormap, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)
    
    
        self.inst_p = addInstructions(0.95, 'P : stop/start the Panda Rotation')
        self.inst_w = addInstructions(0.90, 'W : stop/start the Walk Cycle')
        self.inst_t = addInstructions(0.85, 'T : stop/start the Teapot')
        self.inst_l = addInstructions(0.80, 'L : move light source far or close')
        self.inst_v = addInstructions(0.75, 'V: View the Depth-Texture results')
        self.inst_x = addInstructions(0.70, 'Left/Right Arrow : switch camera angles')
        self.inst_a = addInstructions(0.65, 'Something about A/Z and push bias')
        self.inst_d = addInstructions(0.60, 'Something about D/C and whatever')
    
        base.setFrameRateMeter(1)
        base.setBackgroundColor(0,0,0,1)
    
        base.camLens.setNearFar(1.0,10000)
        base.camLens.setFov(75)
        base.disableMouse()
    
        # Load the scene.
    
        floorTex=loader.loadTexture('maps/envir-ground.jpg')
        cm=CardMaker('')
        cm.setFrame(-2,2,-2,2)
        floor = render.attachNewNode(PandaNode("floor"))
        for y in range(12):
            for x in range(12):
                nn = floor.attachNewNode(cm.generate())
                nn.setP(-90)
                nn.setPos((x-6)*4, (y-6)*4, 0)
        floor.setTexture(floorTex)
        floor.flattenStrong()
    
        self.pandaAxis=render.attachNewNode('panda axis')
        self.pandaModel=Actor.Actor('panda-model',{'walk':'panda-walk4'})
        self.pandaModel.reparentTo(self.pandaAxis)
        self.pandaModel.setPos(9,0,0)
        self.pandaModel.setShaderInput("scale",0.01,0.01,0.01,1.0)
        self.pandaWalk = self.pandaModel.actorInterval('walk',playRate=1.8)
        self.pandaWalk.loop()
        self.pandaMovement = self.pandaAxis.hprInterval(20.0,Point3(-360,0,0),startHpr=Point3(0,0,0))
        self.pandaMovement.loop()
    
        self.teapot=loader.loadModel('teapot')
        self.teapot.reparentTo(render)
        self.teapot.setPos(0,-20,10)
        self.teapot.setShaderInput("texDisable",1,1,1,1)
        self.teapotMovement = self.teapot.hprInterval(50,Point3(0,360,360))
        self.teapotMovement.loop()
    
        self.accept('escape',sys.exit)
    
        self.accept("arrow_left", self.incrementCameraPosition, [-1])
        self.accept("arrow_right", self.incrementCameraPosition, [1])
        self.accept("p", self.toggleInterval, [self.pandaMovement])
        self.accept("P", self.toggleInterval, [self.pandaMovement])
        self.accept("t", self.toggleInterval, [self.teapotMovement])
        self.accept("T", self.toggleInterval, [self.teapotMovement])
        self.accept("w", self.toggleInterval, [self.pandaWalk])
        self.accept("W", self.toggleInterval, [self.pandaWalk])
        self.accept("v", base.bufferViewer.toggleEnable)
        self.accept("V", base.bufferViewer.toggleEnable)
        self.accept("l", self.incrementLightPosition, [1])
        self.accept("L", self.incrementLightPosition, [1])
        self.accept("o", base.oobe)
        self.accept("d", self.adjustConcentration, [0.05])
        self.accept("D", self.adjustConcentration, [0.05])
        self.accept("c", self.adjustConcentration, [-0.05])
        self.accept("C", self.adjustConcentration, [-0.05])
        self.accept('a',self.adjustPushBias,[1.1])
        self.accept('A',self.adjustPushBias,[1.1])
        self.accept('z',self.adjustPushBias,[0.9])
        self.accept('Z',self.adjustPushBias,[0.9])
    
       
        self.LCam=base.makeCamera(LBuffer)
        self.LCam.node().setScene(render)
        self.LCam.node().getLens().setFov(40)
        self.LCam.node().getLens().setNearFar(1,100)
    
        # default values
        self.pushBias=0.04
        self.ambient=0.2
        self.cameraSelection = 0
        self.lightSelection = 0
        self.concentration = 1.0
    
        # setting up shader
        render.setShaderInput('light',self.LCam)
        render.setShaderInput('Ldepthmap',Ldepthmap)
        render.setShaderInput('ambient',self.ambient,0,0,1.0)
        render.setShaderInput('texDisable',0,0,0,0)
        render.setShaderInput('scale',1,1,1,1)
    
        # Put a shader on the Light camera.
        lci = NodePath(PandaNode("Light Camera Initializer"))
        lci.setShader(Shader.load('caster-exp.sha'))
        self.LCam.node().setInitialState(lci.getState())
    
        # Put a shader on the Main camera.
        mci = NodePath(PandaNode("Main Camera Initializer"))
        mci.setShader(Shader.load('shadow-exp.sha'))
        base.cam.node().setInitialState(mci.getState())
    
        self.incrementCameraPosition(0)
        self.incrementLightPosition(0)
        self.adjustPushBias(1.0)
        self.adjustConcentration(0.0)
    
# end of __init__

    def toggleInterval(self, ival):
        if (ival.isPlaying()):
            ival.pause()
        else:
            ival.resume()

    def incrementCameraPosition(self,n):
        self.cameraSelection = (self.cameraSelection + n) % 6
        if (self.cameraSelection == 0):
            base.cam.reparentTo(render)
            base.cam.setPos(30,-45,26)
            base.cam.lookAt(0,0,0)
            self.LCam.node().hideFrustum()
        if (self.cameraSelection == 1):
            base.cam.reparentTo(self.pandaModel)
            base.cam.setPos(7,-3,9)
            base.cam.lookAt(0,0,0)
            self.LCam.node().hideFrustum()
        if (self.cameraSelection == 2):
            base.cam.reparentTo(self.pandaModel)
            base.cam.setPos(-7,-3,9)
            base.cam.lookAt(0,0,0)
            self.LCam.node().hideFrustum()
        if (self.cameraSelection == 3):
            base.cam.reparentTo(render)
            base.cam.setPos(7,-23,12)
            base.cam.lookAt(self.teapot)
            self.LCam.node().hideFrustum()
        if (self.cameraSelection == 4):
            base.cam.reparentTo(render)
            base.cam.setPos(-7,-23,12)
            base.cam.lookAt(self.teapot)
            self.LCam.node().hideFrustum()
        if (self.cameraSelection == 5):
            base.cam.reparentTo(render)
            base.cam.setPos(1000,0,195)
            base.cam.lookAt(0,0,0)
            self.LCam.node().showFrustum()
  
    def incrementLightPosition(self,n):
        self.lightSelection = (self.lightSelection + n) % 2
        if (self.lightSelection == 0):
            self.LCam.setPos(0,-40,25)
            self.LCam.lookAt(0,-10,0)
            self.LCam.node().getLens().setNearFar(1,100)
        if (self.lightSelection == 1):
            self.LCam.setPos(0,-600,200)
            self.LCam.lookAt(0,-10,0)
            self.LCam.node().getLens().setNearFar(500,1000)
  
    def shaderSupported(self):
        return base.win.getGsg().getSupportsBasicShaders() and \
               base.win.getGsg().getSupportsDepthTexture() and \
               base.win.getGsg().getSupportsShadowFilter()
  
    def adjustPushBias(self,inc):
        self.pushBias *= inc
        self.inst_a.setText('A/Z: Increase/Decrease the Push-Bias [%F]' % self.pushBias)
        render.setShaderInput('push',self.pushBias,self.pushBias,self.pushBias,0)
  
    def adjustConcentration(self,inc):
        self.concentration *= (1.0+inc)
        if (self.concentration < 0.1): self.concentration = 0.1
        self.inst_d.setText('D/C: Increase/Decrease the Pixel-Concentration [%F]' % self.concentration)
        render.setShaderInput('concentration',self.concentration,1.0+self.concentration*0.1,0,0)


World()
run()
