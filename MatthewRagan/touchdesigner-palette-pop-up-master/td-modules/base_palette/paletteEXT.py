
class PaletteExplorer:

	def __init__(self, myop):
		self.MyOp 					= myop
		self.PaletteWindowCOMP 		= op('window_palette')
		self.PlacementWindowCOMP 	= op('window_placement')
		self.SelectContainer 		= op('container_palette_widget/container_body/container_selected_palette')
		self.MouseClickDAT 			= op('chopexec_click')

		# last selected TOX info
		self.LastSelectedToxPath 	= tdu.Dependency(None)
		self.LastSelectedToxName 	= tdu.Dependency(None)
		pass

	def PaletteWindow(self, state):

		if state:
			self.PaletteWindowCOMP.par.winopen.pulse()
		else:
			self.PaletteWindowCOMP.par.winclose.pulse()

		pass

	def PlacementWindow(self, state):
		if state:
			self.PlacementWindowCOMP.par.winopen.pulse()
		else:
			self.PlacementWindowCOMP.par.winclose.pulse()

		pass
	
	def FindToxToLoad(self, info):
		row 			= info.get('row')
		TOXPath 	 	= None

		lister 			= info.get('ownerComp').parent(2)
		folderDAT 		= info.get('ownerComp').parent(3).op('folder1')
		folderRowIndex 	= (row+1) + ((lister.digits - 1) * self.SelectContainer.par.Numrows)
		TOXPath 		= folderDAT[ folderRowIndex, 'path']
		TOXName 		= folderDAT[ folderRowIndex, 'name']

		self.LastSelectedToxPath.val = TOXPath
		self.LastSelectedToxName.val = TOXName
		self.PaletteWindow(False)
		return

	def GetCurrentNetworkLocation(self):
		currentPane = ui.panes[ui.panes.current]
		networkPath = currentPane.owner
		return networkPath

	def GetCurrentPane(self):
		return ui.panes[ui.panes.current]

	def CreatePaletteTOX(self):
		OpBuffer 		= self.OpBufferCreate()
		networkPath 	= self.GetCurrentNetworkLocation()

		paletteTOX 		= OpBuffer.loadTox(self.LastSelectedToxPath.val)
		paletteTOX.name = "tempTOX"
		targetOp 		= paletteTOX.findChildren(type=COMP, depth=1)[0]

		# place template
		template 		= OpBuffer.copy(targetOp)
		template.nodeX 	= 200
		template.nodeY 	= 0

		# destroy containing op
		paletteTOX.destroy()

		# Use TD's built in op placement toolkit
		self.GetCurrentPane().placeOPs([template])

		# nuke our temp base
		# self.OpBufferDestroy(OpBuffer)

		pass

	def OpBufferCreate(self):
		
		OpBuffer 		= op('/sys/base_tmp')

		if OpBuffer == None:
			OpBuffer 		= op('/sys').create(baseCOMP)
			OpBuffer.name 	= 'base_tmp'
			OpBuffer.nodeX 	= 0
			OpBuffer.nodeY 	= 600

		return OpBuffer
	
	def OpBufferDestroy(self, OpBuffer):
		OpBuffer.destroy()
		pass

	def PlacePaletteTox(self, info):
		self.FindToxToLoad(info)
		self.CreatePaletteTOX()
		
		pass