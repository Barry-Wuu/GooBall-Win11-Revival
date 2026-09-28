// Glass with fresnel reflection & transparency...
// Tested on: ATI Radeon Mobility

SHADER "Liquids/nonref waterplane" { 
	Properties {
		_Color ("Water color", COLOR)  = ( .172 , .463 , .435 , 1)
		_horizonColor ("horizon color", COLOR)  = ( .172 , .463 , .435 , 1)
		_bScale ("Bump scale", Range (0,1)) = .5
		_BumpPeturb ("Bump strength", Range (0,300)) = 200
		_BumpPeturb2 ("Bump strength2", Range (0,1)) = 1
		_MainTex ("Main texture", 2D) = ""
		_ReflectionTex ("Environment Reflection", RECT) = "spheremap.jpg"
		_ColorControl ("Color ramp (RGB) fresnel (A) ", 2D) = ""
		_ColorControlCube ("Color cube (RGB) fresnel (A) ", Cube) = "" 
		_BumpMap ("Bumpmap (RGB) ", 2D) = ""
	}  
	// -----------------------------------------------------------
	// ARB_FP
	// -----------------------------------------------------------
	SUBSHADER { 
		Pass { 

Program "" {
SubProgram {
  Properties {
    BumpParm ("Wave speed (map1 x, y, map2 x, y)", vector) = (1,1,1,1)
  }
  bind "vertex", ATTR0
  bind "normal", ATTR1
  Local 10, [_ObjectSpaceCameraPos]
  Local 2, [BumpParm]
  Local 5, [_Time]
  Local 3, ([_bScale],0,0,0)

  "!!ARBvp1.0
  PARAM c53 = { 0.4, 0.5, 1, 1 };
  PARAM c55 = { 128, 0, 0, 128 };
  PARAM c56 = { 0, -128, 0, 128 };
  PARAM c57 = { 0, 0, 0.5, 0.5 };
  PARAM c58 = { 0, 0, 0, 1 };
  PARAM c54 = { 0, 2, 3, 0 };
  TEMP R0, R1;
  ATTRIB v1 = vertex.attrib[1];
  ATTRIB v0 = vertex.attrib[0];
  PARAM c10 = program.local[10];
  PARAM c2 = program.local[2];
  PARAM c5 = program.local[5];
  PARAM c3 = program.local[3];
  PARAM s259[4] = { state.matrix.mvp };
  	DP4 R1.x, s259[0], v0;
  	DP4 R1.y, s259[1], v0;
  	DP4 R1.z, s259[2], v0;
  	DP4 R1.w, s259[3], v0;
  	MOV result.fogcoord.x, R1.z;
  	MOV result.position, R1;
  	MOV R0.x, c5;
  	MUL R0, R0.x, c2;
  	MAD R0, v0.xzxz, c3.x, R0;
  	MOV result.texcoord[2], R0.wzww;
  	MUL result.texcoord[1], R0, c53;
  	ADD R0.yzw, c10.xxyz, -v0.xxyz;
  	DP3 R0.x, R0.yzwy, R0.yzwy;
  	RSQ R0.x, R0.x;
  	MUL R0, R0.x, R0.yzwy;
  	MOV result.texcoord[3].xyz, R0.xzyw;
  	DP4 result.texcoord[0].x, c55.xyyx, R1;
  	DP4 result.texcoord[0].y, c56.xyxw, R1;
  	DP4 result.texcoord[0].z, c57.xxzz, R1;
  	MOV result.texcoord[0].w, R1.w;
  END
  	"
}

}
Program "" {
SubProgram {
  Local 0, ([_BumpPeturb],0,0,0)
  Local 1, [_horizonColor]

  "!!ARBfp1.0
OPTION ARB_precision_hint_fastest;
OPTION ARB_fog_exp2;
PARAM c[2] = { program.local[0..1] };
PARAM c3 = { 1, 0,0,0 };

TEMP R0;
TEMP R1;
TEX R0, fragment.texcoord[1], texture[1], 2D;
TEX R1, fragment.texcoord[2], texture[2], 2D;
ADD R0, R0, R1;
SUB R0, R0, c3.xxxx;			# totalbump = bump1 + bump2 - 1

DP3 R1, fragment.texcoord[3], R0;	# fresnel = dot (viewer-pos, totalbump)

#MAD R0.xyzw, R0, c[0].xxxy, fragment.texcoord[0];	# uv = _BumpAmt * totalbump + uv

TEX R1, R1, texture[3], 2D;		# lookup water color & reflection strength

#TXP R0, R0, texture[0], RECT;	# lookup reflection
LRP result.color.rgb, R1.a, c[1], R1;
#LRP result.color.rgb, R1.a, R0, R1;
MUL result.color.a, R0.a, R1.a;
END
  	"
}}

			SetTexture [_BumpMap] { combine texture }
			SetTexture [_BumpMap] {combine texture, previous alpha * texture alpha  }
			SetTexture [_BumpMap] {combine texture, previous alpha * texture alpha  }
			SetTexture [_ColorControl] {combine texture, previous alpha * texture alpha  }
  		}
	}

	//  ------------------------------------------------------------
	// R9000
	//  ------------------------------------------------------------
	SUBSHADER { 
		Pass { 
Program "" {
SubProgram {
  Properties {
    BumpParm ("Wave speed (map1 x, y, map2 x, y)", vector) = (1,1,1,1)
  }
  bind "vertex", ATTR0
  bind "normal", ATTR1
  Local 10, [_ObjectSpaceCameraPos]
  Local 2, [BumpParm]
  Local 5, [_Time]
  Local 3, ([_bScale],0,0,0)

  "!!ARBvp1.0
  PARAM c53 = { 0.4, 0.5, 1, 1 };
  PARAM c55 = { 4, 0, 0, 4 };
  PARAM c56 = { 0, -4, 0, 4 };
  PARAM c57 = { 0, 0, 0.5, 0.5 };
  PARAM c58 = { 0, 0, 0, 1 };
  PARAM c54 = { 0, 2, 3, 0 };
  TEMP R0, R1;
  ATTRIB v1 = vertex.attrib[1];
  ATTRIB v0 = vertex.attrib[0];
  PARAM c10 = program.local[10];
  PARAM c2 = program.local[2];
  PARAM c5 = program.local[5];
  PARAM c3 = program.local[3];
  PARAM s259[4] = { state.matrix.mvp };
  	DP4 R1.x, s259[0], v0;
  	DP4 R1.y, s259[1], v0;
  	DP4 R1.z, s259[2], v0;
  	DP4 R1.w, s259[3], v0;
  	MOV result.fogcoord.x, R1.z;
  	MOV result.position, R1;
  	MOV R0.x, c5;
  	MUL R0, R0.x, c2;
  	MAD R0, v0.xzxz, c3.x, R0;
  	MOV result.texcoord[2], R0.wzww;
  	MUL result.texcoord[1], R0, c53;
  	ADD R0.yzw, c10.xxyz, -v0.xxyz;
  	DP3 R0.x, R0.yzwy, R0.yzwy;
  	RSQ R0.x, R0.x;
  	MUL R0, R0.x, R0.yzwy;
  	MOV result.texcoord[3].xyz, R0.xzyw;
  	DP4 result.texcoord[0].x, c55.xyyx, R1;
  	DP4 result.texcoord[0].y, c56.xyxw, R1;
  	DP4 result.texcoord[0].z, c57.xxzz, R1;
  	MOV result.texcoord[0].w, R1.w;
  END
  	"
}

}

Program "" {
SubProgram {
  Local 0, ([_BumpPeturb2],0,0,0)
  Local 1, [_horizonColor]

"!!ATIfs1.0
StartConstants;
	CONSTANT c0 = program.local[0];
	CONSTANT c1 = program.local[1];
	CONSTANT c2 = { 1, 0.0, 0.03225, 1 };
EndConstants;

StartPrelimPass;
	PassTexCoord r0, t0.stq_dq;
	SampleMap r1, t1.str;	# normalMap1
	SampleMap r2, t2.str;	# normalMap2
	PassTexCoord r3, t3.str;
	# r0.rg = Reflection coord
	ADD r2, r1.bias, r2.bias;		# totalbump = bump1 + bump2

	DOT3 r3, r2, r3;				# r4.a = fresnel  [ dot (totalbump, viewer-pos)
	
#	MAD r0.rg, r2, c0.r, r0;		# uv += totalbump

#	MOV r0.b, c2.b;				# use perspective divide to scale refmap up to size
	
EndPass;

StartOutputPass;
 	SampleMap r3, r3.str;

	LERP r0.rgb, r3.a, c1, r3;	# 	Fade in reflection
	MUL r0.a, r0.a, r3.a;		# Make glossed reflections glow
EndPass;
" 
}
}
			SetTexture [_BumpMap] { combine texture }
			SetTexture [_BumpMap] {combine texture, previous alpha * texture alpha  }
			SetTexture [_BumpMap] {combine texture, previous alpha * texture alpha  }
			SetTexture [_ColorControl] {combine texture, previous alpha * texture alpha  }
  		}
	}
	//  ------------------------------------------------------------
	// R7k, Geforce3,4
	//  ------------------------------------------------------------
	SUBSHADER {
		Pass { 
			SetTexture [_ColorControlCube] {combine texture   Matrix [_Reflection] }
			SetTexture [_BumpMap] {
				combine previous, previous +- texture
			}
			SetTexture [_BumpMap] { 
				ConstantColor [_horizonColor]
				combine constant lerp (previous) previous, previous * texture DOUBLE
			}
      		}
	}
	//  ------------------------------------------------------------
	// Geforce MX 
	//  ------------------------------------------------------------
	SUBSHADER { 
		Pass { 
			SetTexture [_ColorControlCube] {combine texture   Matrix [_Reflection] }
			SetTexture [_BumpMap] {
				combine previous, previous +- texture
			}
      		}
		Pass { 
			Blend DstAlpha OneMinusDstAlpha
			Color [_horizonColor]
      		}
	}
	//  ------------------------------------------------------------
	// Rage128 
	//  ------------------------------------------------------------
	SUBSHADER { 
		Pass { 
			SetTexture [_MainTex] {
				constantColor (.1,.1,.1, 1)
				combine texture * constant alpha
			}
			SetTexture [_BumpMap] {
				combine previous * texture alpha
			}
      		}
	}
}
