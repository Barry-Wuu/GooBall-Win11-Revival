// Glass with fresnel reflection & transparency...


SHADER "Water/Underwater" { 


	Properties { 
		_Color ("Water color", COLOR)  = ( .172 , .463 , .435 , 1) 
		_RefColor ("Reflection color", COLOR)  = ( .172 , .463 , .435 , 1) 
		_MainTex ("Main texture", 2D) = "" {} 
		_CausticColor ("Caustics color", COLOR) = (.8, .8, .8,1)
		_ReflectionMap ("Environment Reflection", 2D) = "spheremap.jpg"
		_ColorControl ("Color ramp (RGB) fresnel (A) ", 2D) = ""
		_ColorControlCube ("Color Cube (RGB)", Cube) = ""
	} 

	// Geforce3+, R9000+
	SUBSHADER { 
		TexCount 4
		Pass { 
			Cull Front
Program "" {
SubProgram {
  Properties {
    horizonColor ("Water color at horizon", color) = (0.615,0.796,0.876,1)
    uvParams ("Uv scale, Uv pertubation, normal bending, refraction.", vector) = ( 10, .02, .03,1)
    waveSpeed ("Waves frequence (waves/time)", vector) = (0.2, 0.15, 0.4, 0.4)
    waveDirY ("Waves Y dir + length", vector) = (0.0, 1.5, -7, 1)
    waveDirX ("Waves X dir + length", vector) = (-2.5, 0.0, 7, 8)
    waveHeights ("Waves heights", vector) = (.8, 1, .1, .05)
  }
  bind "vertex", ATTR0
  bind "normal", ATTR1
  bind "texcoord", ATTR2
  Local 6, [horizonColor]
  Local 55, [_Reflection_0]
  Local 56, [_Reflection_1]
  Local 57, [_Reflection_2]
  Local 5, [uvParams]
  Local 2, [waveSpeed]
  Local 4, [waveDirY]
  Local 3, [waveDirX]
  Local 1, [_waveTime]
  Local 0, [waveHeights]

  "!!ARBvp1.0
  PARAM c59 = { 1, -0.161616, 0.0083333, -0.00019841 };
  PARAM c60 = { -0.5, 0.0416667, -0.00138889, 2.48016e-05 };
  PARAM c58 = { 1.02, 0.5, 6.28319, 0 };
  PARAM c62 = { 0, 0, 0, 1 };
  PARAM c61 = { 2, 0, 0, 0 };
  TEMP R0, R1, R2, R3, R4, R5, R6, R7, R8;
  ATTRIB v2 = vertex.attrib[2];
  ATTRIB v1 = vertex.attrib[1];
  ATTRIB v0 = vertex.attrib[0];
  PARAM c6 = program.local[6];
  PARAM c55[3] = { program.local[55..57] };
  PARAM s631[4] = { state.matrix.modelview[0].invtrans };
  PARAM s223[4] = { state.matrix.modelview[0] };
  PARAM s259[4] = { state.matrix.mvp };
  PARAM c5 = program.local[5];
  PARAM c2 = program.local[2];
  PARAM c4 = program.local[4];
  PARAM c3 = program.local[3];
  PARAM c1 = program.local[1];
  PARAM c0 = program.local[0];
  	MUL R0, v2.y, c4;
  	MAD R0, v2.x, c3, R0;
  	ADD R0, c1, R0;
  	FRC R0, R0;
  	MOV R7, c58;
  	MAD R0, R0, R7.x, -R7.y;
  	MUL R6, R0, R7.z;
  	MUL R5, R6, R6;
  	MUL R0, R5, R6;
  	MUL R4, R0, R6;
  	MUL R1, R4, R6;
  	MUL R3, R1, R6;
  	MUL R2, R3, R6;
  	MAD R0, R0, c59.y, R6;
  	MAD R0, R1, c59.z, R0;
  	MAD R0, R2, c59.w, R0;
  	DP4 R0.x, R0, c0;
  	MOV R1.xyz, v1;
  	MAD R0.xyz, R1.xyzx, R0.x, v0.xyzx;
  	MOV R0.w, v0;
  	DP4 R8.x, s259[0], R0;
  	DP4 R8.y, s259[1], R0;
  	DP4 R8.z, s259[2], R0;
  	DP4 R8.w, s259[3], R0;
  	MOV result.fogcoord.x, R8.z;
  	MOV result.position, R8;
  	MOV result.texcoord[1].zw, c62;
  	MUL result.texcoord[1].xy, v2.xyxx, c5.x;
  	MUL R6, R2, R6;
  	MAD R2, R5, -R7.y, c59.x;
  	MAD R2, R4, c60.y, R2;
  	MAD R2, R3, c60.z, R2;
  	MAD R2, R6, c60.w, R2;
  	MUL R3, R2, c0;
  	DP4 R2.x, R3, c3;
  	DP4 R2.y, R3, c4;
  	MAD R2.xyw, R2.xyxx, c5.z, R1.xzxx;
  	MOV R1.xz, R2.xyyw;
  	DP3 R1.w, R1.xyzx, R1.xyzx;
  	RSQ R1.w, R1.w;
  	MUL R1.xyz, R1.w, R1.xyzx;
  	DP3 R3.x, s631[0].xyzx, R1.xyzx;
  	DP3 R3.y, s631[1].xyzx, R1.xyzx;
  	DP3 R3.z, s631[2].xyzx, R1.xyzx;
  	MUL R2.xyz, c61.x, R3.xyzx;
  	DP4 R1.x, s223[0], R0;
  	DP4 R1.y, s223[1], R0;
  	DP4 R1.z, s223[2], R0;
  	DP4 R1.w, s223[3], R0;
  	DP4 R0.x, R1, R1;
  	RSQ R0.x, R0.x;
  	MUL R0.yzw, R0.x, R1.xxyz;
  	DP3 R0.x, R3.xyzx, R0.yzwy;
  	MAD R1.xyz, -R2.xyzx, R0.x, R0.yzwy;
  	DP3 R0.x, c55[0].xyzx, R1.xyzx;
  	DP3 R0.y, c55[1].xyzx, R1.xyzx;
  	DP3 R0.z, c55[2].xyzx, R1.xyzx;
  	MOV result.texcoord[2].xyz, R0;
  	MOV result.texcoord[0].x, R0.y;
  	MOV result.texcoord[0].y, R7.w;
  	MOV result.texcoord[0].zw, c59.x;
  	MOV result.color.front.primary, c6;
  END
  	"
}

}
			SetTexture [_ColorControl] {
				constantColor [_Color]	
				combine primary lerp (texture) constant, ONE - texture 
			}
			SetTexture [_MainTex] {
				constantColor [_CausticColor]
				combine constant * texture alpha + previous, constant
			}
 			SetTexture [_ReflectionMap] { 
 				constantColor [_RefColor] 
 				combine constant * texture alpha + previous , constant}
      		}
	}
	//  ------------------------------------------------------------
	// Radeon 7000 
	//  ------------------------------------------------------------
	SUBSHADER { 
		Pass { 
			Cull Front
			SetTexture [_ColorControlCube] {
				combine texture 
				Matrix [_Reflection]
			}
			SetTexture [_MainTex] {
				constantColor [_CausticColor]
				combine previous * texture alpha DOUBLE, previous
			}
		}
	}

	// ATI RAGE 128
	SUBSHADER { 
		Pass { 
			Cull Front
			Color [_Color]
			SetTexture [_MainTex] {
				constantColor [_CausticColor]
				combine constant * texture alpha DOUBLE
			}
			SetTexture [_MainTex] {
				constantColor [_CausticColor]
				combine previous + primary
			}
		}
	}
}