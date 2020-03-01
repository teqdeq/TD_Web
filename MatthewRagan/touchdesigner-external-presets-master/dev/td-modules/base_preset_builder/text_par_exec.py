# me - this DAT
# par - the Par object that has changed
# val - the current value
# prev - the previous value
# 
# Make sure the corresponding toggle is enabled in the Parameter Execute DAT.

def onValueChange(par, prev):
	return

def onPulse(par):
	if par.name == 'Setuppresets':
		parent().Default_presets_file()
	
	elif par.name == 'Savetofile':
		parent().Save_presets()

	elif par.name == "Loadfromfile":
		parent().Load_presets_file()
	
	elif par.name == "Recordscenepreset":
		parent().Add_scene_preset()
	
	elif par.name == "Delete":
		parent().Del_preset(parent().par.Existingpresets.menuLabels[parent().par.Existingpresets.menuIndex])
	
	elif par.name == "Load":
		parent().Load_scene_preset()
		print("Load Preset")
	
	else:
		pass
	return

def onExpressionChange(par, val, prev):
	return

def onExportChange(par, val, prev):
	return

def onEnableChange(par, val, prev):
	return

def onModeChange(par, val, prev):
	return
	