##########################################################################
#
#  Copyright (c) 2011, Image Engine Design Inc. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#     * Neither the name of Image Engine Design nor the names of any
#       other contributors to this software may be used to endorse or
#       promote products derived from this software without specific prior
#       written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##########################################################################

import os
import sys
import shutil
import unittest
import IECore

class TestRelativePreset( unittest.TestCase ) :

	def testSparseSimpleChanges( self ) :
	
		def createTestObj():
			testObj = IECore.Parameterised( "testParameterised1" )
			testObj.parameters().addParameters(
				[
					IECore.BoolParameter( "a", "", True ),	
					IECore.FloatParameter( "b", "", 1.0 ),	
				]
			)
			return testObj
			
		def createTestObj2():
			testObj2 = IECore.Parameterised( "testParameterised2" )
			testObj2.parameters().addParameters(
				[
					IECore.BoolParameter( "a", "", True ),
					IECore.FloatParameter( "c", "", 0.0	),	
				]
			)
			return testObj2
		
		testObjA = createTestObj()
		testObjB = createTestObj()
		testObjB["a"] = False
		r = IECore.RelativePreset( testObjB.parameters(), testObjA.parameters() )

		testObj2 = createTestObj2()

		self.failUnless( r.applicableTo( testObjA, testObjA.parameters() ) )
		self.failUnless( r.applicableTo( testObj2, testObj2.parameters() ) )

		r( testObjB, testObjB.parameters() )
		
		self.assertEqual( testObjB.parameters()["a"].getTypedValue(), False )
		self.assertEqual( testObjB.parameters()["b"].getTypedValue(), 1.0 )

		r( testObj2, testObj2.parameters() )
		
		self.assertEqual( testObj2.parameters()["a"].getTypedValue(), False )
		self.assertEqual( testObj2.parameters()["c"].getTypedValue(), 0.0 )

		r = IECore.RelativePreset( testObjB.parameters() )
		testObjB["a"] = True
		testObjB["b"] = 2.0
		r( testObjB, testObjB.parameters() )
		self.assertEqual( testObjB.parameters()["a"].getTypedValue(), False )
		self.assertEqual( testObjB.parameters()["b"].getTypedValue(), 1.0 )

		
	def testClasses( self ) :
	
		def createTestObj():
			testObj = IECore.Parameterised( "testParameterised1" )
			testObj.parameters().addParameters(
				[
					IECore.BoolParameter( "a", "", True ),	
					IECore.ClassParameter( "b", "", "IECORE_OP_PATHS" ),	
				]
			)
			return testObj
		
		def createTestObj2():
			testObj2 = IECore.Parameterised( "testParameterised2" )
			testObj2.parameters().addParameters(
				[
					IECore.ClassParameter( "b", "",	"IECORE_OP_PATHS" ),	
				]
			)
			return testObj2

		testObjA = createTestObj()
		testObjB = createTestObj()
		testObj2 = createTestObj2()

		testObjB["b"].setClass( "maths/multiply", 2 )
		
		classes1 = testObjB.parameters()["b"].getClass( True )
		classes2 = testObj2.parameters()["b"].getClass( True )
		self.assertNotEqual( classes1[1:], classes2[1:] )

		r = IECore.RelativePreset( testObjB.parameters(), testObjA.parameters() )

		self.failUnless( r.applicableTo( testObjB, testObjB.parameters() ) )
		self.failUnless( r.applicableTo( testObj2, testObj2.parameters() ) )

		r( testObj2, testObj2.parameters() )
		
		classes1 = testObjB.parameters()["b"].getClass( True )
		classes2 = testObj2.parameters()["b"].getClass( True )
		
		self.assertEqual( classes1[1:], classes2[1:] )

		r = IECore.RelativePreset( testObjB.parameters() )
		testObjB["a"] = False
		testObjB["b"].setClass("", 0)
		r( testObjB, testObjB.parameters() )
		classes1 = testObjB.parameters()["b"].getClass( True )
		self.assertEqual( classes1[1:], classes2[1:] )
		self.assertEqual( testObjB["a"].getTypedValue(), True )

	def testClassVectors( self ) :
	
		def createTestObj() :
			testObj = IECore.Parameterised( "testParameterised1" )
			testObj.parameters().addParameters(
				[
					IECore.BoolParameter( "a", "", True ),	
					IECore.ClassVectorParameter( "b", "", "IECORE_OP_PATHS" ),	
				]
			)
			return testObj

		testObjA = createTestObj()
		testObjB = createTestObj()

		testObjB.parameters()["b"].setClasses(
			[
				( "mult", "maths/multiply", 2 ),
				( "coIO", "compoundObjectInOut", 1 ),
			]
		)

		def createTestObj2():
			testObj2 = IECore.Parameterised( "testParameterised2" )
			testObj2.parameters().addParameters(
				[
					IECore.ClassVectorParameter( "b", "", "IECORE_OP_PATHS" ),	
				]
			)
			return testObj2

		testObj2 = createTestObj2()
		
		classes1 = [ c[1:] for c in testObjB.parameters()["b"].getClasses( True ) ]
		classes2 = [ c[1:] for c in testObj2.parameters()["b"].getClasses( True ) ]
		
		self.assertNotEqual( classes1, classes2 )
		self.assertEqual( len(classes1), 2 )
		
		r1 = IECore.RelativePreset( testObjB.parameters() )
		r2 = IECore.RelativePreset( testObjB.parameters(), testObjA.parameters() )
		
		self.failUnless( r1.applicableTo( testObjB, testObjB.parameters() ) )
		self.failUnless( r1.applicableTo( testObj2, testObj2.parameters() ) )
		self.failUnless( r2.applicableTo( testObj2, testObj2.parameters() ) )

		r2( testObj2, testObj2.parameters() )
		
		classes2 = [ c[1:] for c in testObj2.parameters()["b"].getClasses( True ) ]
		self.assertEqual( classes1, classes2 )

		# now we reorder ops...
		testObjC = createTestObj()
		classes1.reverse()
		testObjC["b"].setClasses( classes1 )
		r = IECore.RelativePreset( testObjC.parameters(), testObjB.parameters() )

		r( testObj2, testObj2.parameters() )
		classes2 = [ c[1:] for c in testObj2.parameters()["b"].getClasses( True ) ]
		self.assertEqual( classes1, classes2 )

		# now we remove an op
		testObj2["b"].removeClass( "mult" )
		classes2 = [ c[1] for c in testObj2.parameters()["b"].getClasses( True ) ]
		self.assertEqual( classes2, [ "coIO" ] )
		r = IECore.RelativePreset( testObj2.parameters(), testObjB.parameters() )
		r( testObjB, testObjB.parameters() )
		classes1 = [ c[1] for c in testObjB.parameters()["b"].getClasses( True ) ]
		self.assertEqual( classes1, [ "coIO" ] )
		
		# now we add it back
		testObj2["b"].setClass( "mult", "maths/multiply", 2 )
		testObj2["b"].setClass( "another", "maths/multiply", 2 )
		r = IECore.RelativePreset( testObj2.parameters(), testObjB.parameters() )
		r( testObjB, testObjB.parameters() )
		classes1 = [ c[1:] for c in testObjB.parameters()["b"].getClasses( True ) ]
		classes2 = [ c[1:] for c in testObj2.parameters()["b"].getClasses( True ) ]
		self.assertEqual( len(classes2), 3 )
		self.assertEqual( classes1, classes2 )

		# now we replace one of them
		testObj2["b"].setClass( "another", "compoundObjectInOut", 1 )
		r = IECore.RelativePreset( testObj2.parameters(), testObjB.parameters() )
		r( testObjB, testObjB.parameters() )
		classes1 = [ c[1:] for c in testObjB.parameters()["b"].getClasses( True ) ]
		classes2 = [ c[1:] for c in testObj2.parameters()["b"].getClasses( True ) ]
		self.assertEqual( len(classes2), 3 )
		self.assertEqual( classes1, classes2 )

	def testDeepClassVectors( self ) :

		def createParameterised():
			testObj = IECore.Parameterised( "testParameterised1" )
			testObj.parameters().addParameters(
				[
					IECore.BoolParameter( "a", "", True ),	
					IECore.ClassVectorParameter( "b", "", "IECORE_OP_PATHS" ),	
					IECore.BoolParameter( "c", "", False ),	
				]
			)
			testObj.parameters()["b"].setClasses(
				[
					( "p0", "maths/multiply", 2 ),
					( "p1", "compoundObjectInOut", 1 ),
					( "p2", "classVectorParameterTest", 1),
					( "p3", "maths/multiply", 1 ),
					( "p4", "classParameterTest", 1),
				]
			)
			testObj["b"]["p2"]["cv"].setClasses(
				[
					( "p0", "maths/multiply", 2 ),
					( "p1", "compoundObjectInOut", 1 )
				]
			)
			testObj["b"]["p4"]["cp"].setClass( "maths/multiply", 2 )
			return testObj

		testObjA = createParameterised()

		testObjB = createParameterised()

		# test no differences
		r = IECore.RelativePreset( testObjB.parameters(), testObjA.parameters() )
		# the diff should be empty!
		self.assertEqual( r._RelativePreset__data, IECore.CompoundObject() )
		# applying empty diff should not break
		r( testObjB, testObjB.parameters() )
		self.assertEqual( testObjA.parameters().getValue(), testObjB.parameters().getValue() )

		# now we modify the object a lot!!
		testObjB["a"] = False
		testObjB["c"] = True
		testObjB["b"].removeClass( "p1" )
		testObjB["b"].removeClass( "p3" )
		testObjB["b"]["p0"]["a"] = False
		testObjB["b"]["p4"]["cp"]["a"] = 10
		testObjB["b"]["p2"]["cv"]["p0"]["a"] = 20
		testObjB["b"]["p2"]["cv"].setClass("p1", "maths/multiply", 2 )	# replace one op
		testObjB["b"]["p2"]["cv"].setClass("p3", "floatParameter", 1 )	# add one op
		# reoder "b" elements
		order = map( lambda c: c[1:], testObjB["b"].getClasses(True) )
		order.reverse()
		testObjB["b"].setClasses(order)

		# now we apply the changes on an object identical to the original one represented in the basic preset.
		testObj2 = createParameterised()
		r = IECore.RelativePreset( testObjB.parameters(), testObjA.parameters() )
		relPreset = r	# copy this preset, as it's going to be used later on again...
		r( testObj2, testObj2.parameters() )
		self.assertEqual( testObj2.parameters().getValue(), testObjB.parameters().getValue() )
		classes1 = [ c[1:] for c in testObjB.parameters()["b"].getClasses( True ) ]
		classes2 = [ c[1:] for c in testObj2.parameters()["b"].getClasses( True ) ]
		self.assertEqual( len(classes2), 3 )
		self.assertEqual( classes1, classes2 )
		classes1 = [ c[1:] for c in testObjB.parameters()["b"]["p2"]["cv"].getClasses( True ) ]
		classes2 = [ c[1:] for c in testObj2.parameters()["b"]["p2"]["cv"].getClasses( True ) ]
		self.assertEqual( len(classes2), 3 )
		self.assertEqual( classes1, classes2 )
		
		# we test the other way around
		testObj2 = createParameterised()
		r = IECore.RelativePreset( testObj2.parameters(), testObjB.parameters() )
		r( testObjB, testObjB.parameters() )
		self.assertEqual( testObj2.parameters().getValue(), testObjB.parameters().getValue() )
		classes1 = [ c[1:] for c in testObjB.parameters()["b"].getClasses( True ) ]
		classes2 = [ c[1:] for c in testObj2.parameters()["b"].getClasses( True ) ]
		self.assertEqual( len(classes2), 5 )
		self.assertEqual( classes1, classes2 )
		classes1 = [ c[1:] for c in testObjB.parameters()["b"]["p2"]["cv"].getClasses( True ) ]
		classes2 = [ c[1:] for c in testObj2.parameters()["b"]["p2"]["cv"].getClasses( True ) ]
		self.assertEqual( len(classes2), 2 )
		self.assertEqual( classes1, classes2 )

		# now it gets tricky... we try to apply the changes on a different object...
		testObj2 = createParameterised()
		testObj2.parameters().removeParameter("a")		# remove "a"
		testObj2.parameters().removeParameter("c")		# replace "c" by something else
		testObj2.parameters().addParameter( 
			IECore.IntParameter( "c", "", 10 )
		)
		testObj2.parameters().addParameter(				# add new parameter "d"
			IECore.IntParameter( "d", "", 10 )
		)
		testObj2["b"].removeClass("p1")				# we remove "p1" - the same parameter that the preset will try to remove later... it should ignore it
		testObj2["b"].setClass("p3", "compoundObjectInOut", 1 )	# we replace "p3" - the same parameter that the preset will try to remove later... it should not remove because it's a different class.
		testObj2["b"]["p4"]["cp"]["a"] = 30			# we want this value to be replaced by 10 which was the relative change on that parameter
		testObj2["b"]["p2"]["cv"].setClass("p1", "maths/multiply", 1 )	# replace an op that the preset will try to replace too...  but will not because the original class is be different
		testObj2["b"]["p2"]["cv"].setClass("p3", "compoundObjectInOut", 1 )	# add one op that the preset will try to add too... name clashes!

		relPreset( testObj2, testObj2.parameters() )
		
		self.assertEqual( testObj2["c"].getTypedValue(), 10 )	# guarantee that the replaced parameter "c" was not affected by the Preset
		self.assert_( "p3" in testObj2["b"].keys() )			# ok, "p3" was not removed!
		self.assertEqual( testObj2["b"]["p4"]["cp"]["a"].getTypedValue(), 10 )	# ok, the preset changes were applied here
		self.assertEqual( testObj2["b"]["p2"]["cv"].getClass( "p1", True )[2], 1 )	# ok, the Preset did not change this one because it was looking for a compoundObjectInOut class name...
		self.assertEqual( testObj2["b"]["p2"]["cv"].getClass( "p3", True )[1], "compoundObjectInOut" )	# ok, the Preset did not remove the current "p3" parameter...
		self.assertEqual( testObj2["b"]["p2"]["cv"].getClass( "p2", True )[1], "maths/multiply" )	# ok, the Preset added a new parameter "p2" with the "p1" Preset...
		self.assertEqual( testObj2["b"]["p2"]["cv"].getClass( "p4", True )[1], "floatParameter" )	# ok, the Preset added a new parameter "p4" with the "p3" Preset...

if __name__ == "__main__":
	unittest.main()