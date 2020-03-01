'''
Matthew Ragan | matthewragan.com
'''

import json
import os

class Presets:
	'''
		This is a sample class.

		This sample class has several important features that can be described here.


		Notes
		---------------
		Your notes about the class go here
 	''' 	

	def __init__(self, myOp):
		self.MyOp 				= myOp
		self.Json_presets 		= parent().par.Presetsfile
		self.Project_dir 		= project.folder
		self.Td_preset_storage 	= parent().par.Tdpresetstorage
		self.Selected_preset 	= parent().par.Existingpresets
		self.Num_scene_presets 	= tdu.Dependency(0)
		self.Update_num_scenes()
		self.P1_deck			= parent().par.P1deck
		self.P2_deck			= parent().par.P2deck
		print("Presets Init")
		
		pass

	def Update_num_scenes(self):
		self.Num_scene_presets.val = len(op(parent().par.Tdpresetstorage).fetch("presets")['scenes'].keys())
		pass

	def Default_presets_file(self):
		path 				= '{}/data'.format(self.Project_dir)
		preset_file  		= '{}/presets.json'.format(path)

		# check to see if path is already made
		if os.path.isdir(path):
			return_msg 		= "Path already exists | {}".format(path)

		else:
			os.mkdir(path)
			new_preset = open(preset_file, "w")
			new_preset.close()
			parent().par.Presetsfile = 'data/presets.json'
			return_msg 		= "Path and presets.json created | {}".format(path)
		pass

	def Add_scene_preset(self):
		
		# construct dict from pars
		new_pars_dict 	= self.Dict_from_pars(self.MyOp, 'Preset Builder')
		
		# add dict to storage in target operator
		self.Add_preset(new_pars_dict)

		# update list
		self.Update_num_scenes()

		pass

	def Load_scene_preset(self):

		current_preset = self.Load_preset_editor(self.MyOp, 
												self.Selected_preset.menuLabels[self.Selected_preset.menuIndex])
		self.Set_decks()
		pass

	def Set_decks(self):
		
		# current Scenes from builder
		p1_scene 	= parent().par.P1scene.eval()
		p2_scene 	= parent().par.P2scene.eval()

		# Decks
		Deck_p1 	= self.P1_deck.eval()
		Deck_p2 	= self.P2_deck.eval()

		# call deck pars 
		op(Deck_p1).Change_deck(p1_scene)
		op(Deck_p2).Change_deck(p2_scene)
		pass

	def Load_presets_file(self):
		presets_dict = self.Load_json('{}/{}'.format( project.folder, parent().par.Presetsfile.eval()))
		op(self.Td_preset_storage).store('presets', presets_dict)
		pass

	def Dict_from_pars(self, op_with_custom_pars, par_page):
		'''A helper function to convert a set of custom pars into a dictionary.

		Notes
		---------
		This helper function is largely to simplify an approach. Rather than constructing
		a complete dictionary of pars, this method instead accepts an op with custom
		parameters, and a page to pull parameters from. This will then place all parameters
		and values into a dictionary to be used by the Add_preset() method.

		Args
		---------
		op_with_custom_pars (touch op) 	: this is a TouchDesigner operator that has custom
											parameters to be used for building a preset

		par_page (str)					: the string name of the page which contains parameters
											to be converted into a dictionary.

		Returns
		---------
		pars_as_dict (dict) 			: a dictionary where all parameter names are used as keys
											and the par values are used as dictionary values.
		'''

		# make an empty dict to fill up
		pars_as_dict 		= {}

		# loop through all pars from the target op
		for par in op_with_custom_pars.pars():
			# isolate custom pars that are not pulses
			if par.isCustom and not par.isPulse:
				# isolate pars based on page
				if par.page == par_page:
					# debug dummy check
					#print(par.name, par.val, par.style, par.page)

					# add scoped pars to dictionary
					pars_as_dict[par.name] = par.val

		return pars_as_dict

	def Load_preset_editor(self, builder_op, preset_key):
		'''Used to load presets into the builder preset builder UI.

		Notes
		---------
		The ability to load and update an existing preset seems requist for this set of
		functions. This approach uses the builder op, and a preset key to do just this. More
		than anything this extends the existing the pre-set builder approach to allow for 
		less nusance preset building - rather than needing to delete a preset before editing
		this will instead allow for presets to be loaded and changed. 

		Args
		---------
		builder_op (touch op) 	: the op with the custom parameters that have been stored as a preset dict

		preset_key (str)		: the string name of the preset to be retrieved from storage.

		Returns
		---------
		none
		'''		
		preset_target 		= self.Td_preset_storage.eval()
		presets 			= op(preset_target).fetch("presets")["scenes"]

		current_preset 		= presets[preset_key]

		# print(builder_op)

		# passed from preset builder
		# print( "- - - - - PRESET - - - - -")
		# print(preset_key)

		# retreived vals
		# print( "- - - - - vals in preset - - - - -")
		for keys, values in current_preset.items():
			#print( builder_op.pars(keys) )
			builder_op.pars(keys)[0].val = values

		return current_preset.items()

	def Add_preset( self, preset_dict ):
		'''Adds a preset to the strage dictionary "presets".

		Notes
		---------
		This helper function takes a dictionary and appends it to the existing
		"presets" dict in storage. This generalized behavior saves the user the
		headache of sorting all of this out in an execute. Safety measures are
		included to prevent failed attempts. The user is warned when the preset_name
		is missing - this is likey to happen if the user forgets to enter a name
		for the preset. Similarly, there is a warning if you're using the same
		preset name. Rather than write over an existing preset, this will warn
		you not to do this. Should it be ncessary, and update approach could be added.

		Args
		---------
		preset_dict (dict) : The preset dict is a dictioary of keys and values
								that's been constructed from the custom pars of 
								a target op. 

		Returns
		---------
		none
		'''

		preset_target 		= self.Td_preset_storage.eval()
		current_presets 	= op(preset_target).fetch("presets")
		preset_name 		= preset_dict['Scenepresetname']

		user_approval 		= 1

		# warning for missing preset name
		if preset_name == '' or None:
			title 			= "Warning - Missing Preset Name"
			message 		= "It looks like you didn't name your preset"
			buttons 		= ["okay"] 
			ui.messageBox(title, message, buttons=buttons)
			user_approval 	= 0

		# warning for duplicate preset entires
		elif preset_name in list(current_presets.keys()):
			title 			= "Warning - Duplicate Entry"
			message 		= "Whoa there tiger you got a duplicate entry"
			buttons 		= ["Cancel", "Update"] 
			user_approval 	= ui.messageBox(title, message, buttons=buttons)

		# user approval is expected to be true, this could change in the
		# case of possibly overwriting vals in an existing preset
		# we can use the warning above, and the results from the button
		# clicked to determine if we should update storage
		if user_approval:
			# add the new preset to the fetched dictionary and place back in storage.
			new_preset_name 	= preset_name
			current_presets["scenes"][new_preset_name] = preset_dict
			op(preset_target).store('presets', current_presets)
		
		else:
			pass
		# dummy check
		# print("Add_preset printing")		
		pass

	def Del_preset(self, preset_key):
		'''Deletes an entry from storage.

		Notes
		---------
		More than just adding keys, it's important to be able to remove presets that
		are not being used, or present issues. This methods will use the del command
		to revove a given key from storage.

		Args
		---------
		preset_key (str) : the string name of the key to be removed from storage

		Returns
		---------
		none
		'''
		print("Deleting")

		preset_target 		= self.Td_preset_storage.eval()
		current_presets 	= op(preset_target).fetch("presets")
		# safety to ensure that the given key exists in the dictionary
		if preset_key in current_presets['scenes'].keys():

			title 				= "WARNING DELTING PRESET"
			message 			= "You're about to delete the preset {}".format(preset_key)
			buttons 			= ["Cancel", "Okay"]

			# confirmation message to ensure that the user wants to delet the preset
			confirm 			= ui.messageBox(title, message, buttons=buttons)
			if confirm:
				del current_presets['scenes'][preset_key]
				op(preset_target).store("presets", current_presets)
				self.Update_num_scenes()
			else:
				pass

		else:
			pass

		pass

	def Load_json( self, target_path ):
		'''Return a Python dictionary from a json file

		Notes
		---------
		A helper function designed to return an entire dictionary from
		an external json file.

		Args
		---------
		target_path (str) : a string path to be apended to project.folder
						as an important note, the file path should start
						with a forward slash (/) - this avoids the need for
						escape characters with python.

		Returns
		---------
		json_dict (dictionary) : the contents of a json file as a python dictionary
								returns a nonetype object and logs an error message if the
								file cannot be found.
		'''
		target_file 		= target_path
		json_dict			= None

		# check to ensure the file exists before attempting to open
		# returns a nonetype object and logs an error message if the
		# file cannot be found.
		if os.path.isfile( target_file ):
			with open( target_file, 'r' ) as json_file:
				json_dict	= json.load( json_file )

		else:
			error_msg		= self.Missing_file.format( file_name = target_file )
			print( error_msg )
			json_dict		= None

		return json_dict

	def Save_presets( self ):
		'''Saves all presets in Storage out to file as JSON.

		Notes
		---------
		This method is used to save out the contents of the "presets" dictionary
		in storage to file. The method includes some safety measures to ensure
		that the user is aware of the implications of this action - namely
		that the existing file will be over-written. This is the correct 
		behavior, but worth rasing a flag in case the user wants / needs
		to create a back up of the file to swap to at a later date.

		Args
		---------
		none

		Returns
		---------
		none
		'''

		# construct a path to our preset file
		json_presets 		= self.Json_presets.eval()

		# grab presets from storage
		current_presets 	= op(parent().par.Tdpresetstorage).fetch("presets")

		# dict - JSON
		preset_dumps 		= json.dumps( current_presets, 
											sort_keys=True, 
											indent=4, 
											separators=(',', ': '))

		# Confirm overwriting presets
		title 				= "Preset File Overwrite"
		message 			= "You are about to overwrite the existing preset file"
		buttons 			= ["Cancel", "Continue"]
		confirm 			= ui.messageBox( title, message, buttons=buttons)

		# only save if we've said yes
		if confirm:
			# check for file existance, open, write, close
			if os.path.isfile( json_presets ):
				with open(json_presets, 'w') as json_file:
					json_file.write( preset_dumps )
					json_file.close()

			else:
				error_msg	= self.Missing_file.format( file_name = json_presets )
				print(error_msg)
		else:
			pass

		pass