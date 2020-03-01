/* Shared Use License: This file is owned by Derivative Inc. (Derivative) and
 * can only be used, and/or modified for use, in conjunction with 
 * Derivative's TouchDesigner software, and only if you are a licensee who has
 * accepted Derivative's TouchDesigner license or assignment agreement (which
 * also govern the use of this file).  You may share a modified version of this
 * file with another authorized licensee of Derivative's TouchDesigner software.
 * Otherwise, no redistribution or sharing of this file, with or without
 * modification, is permitted.
 */

#include "SmoothstepCHOP.h"

#include <stdio.h>
#include <string.h>
#include <cmath>
#include <assert.h>

#include <algorithm>

// These functions are basic C function, which the DLL loader can find
// much easier than finding a C++ Class.
// The DLLEXPORT prefix is needed so the compile exports these functions from the .dll
// you are creating
extern "C"
{

DLLEXPORT
int32_t
GetCHOPAPIVersion(void)
{
	// Always return CHOP_CPLUSPLUS_API_VERSION in this function.
	return CHOP_CPLUSPLUS_API_VERSION;
}

DLLEXPORT
CHOP_CPlusPlusBase*
CreateCHOPInstance(const OP_NodeInfo* info)
{
	// Return a new instance of your class every time this is called.
	// It will be called once per CHOP that is using the .dll
	return new CPlusPlusCHOPExample(info);
}

DLLEXPORT
void
DestroyCHOPInstance(CHOP_CPlusPlusBase* instance)
{
	// Delete the instance here, this will be called when
	// Touch is shutting down, when the CHOP using that instance is deleted, or
	// if the CHOP loads a different DLL
	delete (CPlusPlusCHOPExample*)instance;
}

};


CPlusPlusCHOPExample::CPlusPlusCHOPExample(const OP_NodeInfo* info) : myNodeInfo(info)
{
	myExecuteCount = 0;
}

CPlusPlusCHOPExample::~CPlusPlusCHOPExample()
{

}

void
CPlusPlusCHOPExample::getGeneralInfo(CHOP_GeneralInfo* ginfo)
{
	// This will cause the node to cook every frame
	ginfo->cookEveryFrameIfAsked = false;
	ginfo->timeslice = false;
	ginfo->inputMatchIndex = 0;
}

bool
CPlusPlusCHOPExample::getOutputInfo(CHOP_OutputInfo* info)
{
	return false;
}

const char*
CPlusPlusCHOPExample::getChannelName(int32_t index, void* reserved)
{
	return "chan1";
}

float clamp(float x, float lowerlimit, float upperlimit) {
	if (x < lowerlimit)
		x = lowerlimit;
	if (x > upperlimit)
		x = upperlimit;
	return x;
}

float linear_clamp(float edge0, float edge1, float x) {

	if (edge1 == edge0) {
		return x > edge1 ? 1. : 0;
	}

	// Scale, bias and saturate x to 0..1 range
	x = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);
	// Evaluate polynomial
	return x;
}
float smoothstep(float edge0, float edge1, float x) {

	if (edge1 == edge0) {
		return x > edge1 ? 1. : 0;
	}

	// Scale, bias and saturate x to 0..1 range
	x = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);
	// Evaluate polynomial
	return x * x * (3. - 2. * x);
}

// with the help of Ken Perlin
float smootherstep(float edge0, float edge1, float x) {

	if (edge1 == edge0) {
		return x > edge1 ? 1. : 0;
	}

	// Scale, and clamp x to 0..1 range
	x = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);
	// Evaluate polynomial
	return x * x * x * (x * (x * 6. - 15.) + 10.);
}

// with the help of Kyle McDonald and Wolfram Alpha
float smootheststep(float edge0, float edge1, float x) {

	if (edge1 == edge0) {
		return x > edge1 ? 1. : 0;
	}

	// Scale, and clamp x to 0..1 range
	x = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);

	float x2 = x * x;
	float x3 = x2 * x;
	float x4 = x3 * x;

	return x4 * (-20. * x3 + 70. * x2 - 84. * x + 35.);
}

void
CPlusPlusCHOPExample::execute(const CHOP_Output* output,
							  OP_Inputs* inputs,
							  void* reserved)
{
	myExecuteCount++;

	if (inputs->getNumInputs() > 0)
	{
		int mode = inputs->getParInt("Mode");
		double edge0, edge1;
		double range1, range2;
	
		bool getParSuccess = false;
		getParSuccess = inputs->getParDouble2("Fromrange", edge0, edge1);
		assert(getParSuccess);
		getParSuccess = inputs->getParDouble2("Torange", range1, range2);
		assert(getParSuccess);

		const OP_CHOPInput* cinput = inputs->getInputCHOP(0);

		for (int i = 0; i < output->numChannels; i++)
		{

			for (int j = 0; j < output->numSamples; j++)
			{

				float v = cinput->getChannelData(i)[j];

				switch (mode)
				{
				case 0: // smoothstep
					v = smoothstep(edge0, edge1, v);
					break;

				case 1: // smootherstep
					v = smootherstep(edge0, edge1, v);
					break;

				case 2:	// smootheststep
					v = smootheststep(edge0, edge1, v);
					break;

				case 3:	// linear clamp
					v = linear_clamp(edge0, edge1, v);
					break;
				}

				// linear remap
				v = range1 + (range2 - range1) * v;

				output->channels[i][j] = v;
			}
		}
	}
}



int32_t
CPlusPlusCHOPExample::getNumInfoCHOPChans()
{
	// We return the number of channel we want to output to any Info CHOP
	// connected to the CHOP. In this example we are just going to send one channel.
	return 2;
}

void
CPlusPlusCHOPExample::getInfoCHOPChan(int32_t index,
										OP_InfoCHOPChan* chan)
{
	// This function will be called once for each channel we said we'd want to return
	// In this example it'll only be called once.

	if (index == 0)
	{
		chan->name = "executeCount";
		chan->value = (float)myExecuteCount;
	}
}

bool		
CPlusPlusCHOPExample::getInfoDATSize(OP_InfoDATSize* infoSize)
{
	infoSize->rows = 1;
	infoSize->cols = 2;
	// Setting this to false means we'll be assigning values to the table
	// one row at a time. True means we'll do it one column at a time.
	infoSize->byColumn = false;
	return true;
}

void
CPlusPlusCHOPExample::getInfoDATEntries(int32_t index,
										int32_t nEntries,
										OP_InfoDATEntries* entries)
{
	// It's safe to use static buffers here because Touch will make it's own
	// copies of the strings immediately after this call returns
	// (so the buffers can be reuse for each column/row)
	static char tempBuffer1[4096];
	static char tempBuffer2[4096];

	if (index == 0)
	{
		// Set the value for the first column
#ifdef WIN32
		strcpy_s(tempBuffer1, "executeCount");
#else // macOS
        strlcpy(tempBuffer1, "executeCount", sizeof(tempBuffer1));
#endif
		entries->values[0] = tempBuffer1;

		// Set the value for the second column
#ifdef WIN32
		sprintf_s(tempBuffer2, "%d", myExecuteCount);
#else // macOS
        snprintf(tempBuffer2, sizeof(tempBuffer2), "%d", myExecuteCount);
#endif
		entries->values[1] = tempBuffer2;
	}
}

void
CPlusPlusCHOPExample::setupParameters(OP_ParameterManager* manager)
{
	// Input range
	{
		OP_NumericParameter	np;

		np.name = "Fromrange";
		np.label = "From Range";
		np.defaultValues[0] = 0.0;
		np.defaultValues[1] = 1.0;
		np.minSliders[0] =  0.0;
		np.maxSliders[0] =  1.0;
		np.minSliders[1] = 0.0;
		np.maxSliders[1] = 1.0;
		
		OP_ParAppendResult res = manager->appendFloat(np,2);
		assert(res == OP_ParAppendResult::Success);
	}

	// Output range
	{
		OP_NumericParameter	np;

		np.name = "Torange";
		np.label = "To Range";
		np.defaultValues[0] = 0.0;
		np.defaultValues[1] = 1.0;
		np.minSliders[0] = 0.0;
		np.maxSliders[0] = 1.0;
		np.minSliders[1] = 0.0;
		np.maxSliders[1] = 1.0;

		OP_ParAppendResult res = manager->appendFloat(np,2);
		assert(res == OP_ParAppendResult::Success);
	}

	// Mode
	{
		OP_StringParameter	sp;

		sp.name = "Mode";
		sp.label = "Mode";

		sp.defaultValue = "Mode";

		const char *names[] = {"Smoothstep", "Smootherstep", "Smootheststep", "Linearclamp"};
		const char *labels[] = {"Smoothstep", "Smootherstep", "Smootheststep", "Linear Clamp"};

		OP_ParAppendResult res = manager->appendMenu(sp, 4, names, labels);
		assert(res == OP_ParAppendResult::Success);
	}
}

void 
CPlusPlusCHOPExample::pulsePressed(const char* name)
{
}

