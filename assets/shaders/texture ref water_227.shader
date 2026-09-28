// Glass with fresnel reflection & transparency...
// Tested on: ATI Radeon Mobility

SHADER "Liquids/reflective waterplane" { 
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
  Local 5, ([_bScale],0,0,0)
  Local 6, [BumpParm]
  Local 7, [_Time]
  Local 9, [_ObjectSpaceCameraPos]

  "!!ARBvp1.0
  PARAM c[10] = { { 0, 0.5, 128 },
  		state.matrix.mvp,
  		program.local[5..7],
  		{ 0.40000001, 0.5, 1 },
  		program.local[9] };
  TEMP R0;
  TEMP R1;
  TEMP R2;
  DP4 R2.xy, vertex.attrib[0], c[3];
  DP4 R1.w, vertex.attrib[0], c[4];
  MOV R0.z, R2.y;
  MOV R0.w, R1;
  DP4 R0.x, vertex.attrib[0], c[1];
  DP4 R0.y, vertex.attrib[0], c[2];
  MOV R1.x, c[7];
  MOV result.position, R0;
  DP4 result.texcoord[0].z, R0, c[0].xxyy;
  DP4 result.texcoord[0].y, R0, c[0].xzxz;
  DP4 result.texcoord[0].x, R0, c[0].zxxz;
  MUL R0, c[6], R1.x;
  MAD R0, vertex.attrib[0].xzxz, c[5].x, R0;
  ADD R1.xyz, -vertex.attrib[0], c[9];
  DP3 R2.y, R1, R1;
  MUL result.texcoord[1], R0, c[8].xyzz;
  RSQ R0.x, R2.y;
  MOV result.texcoord[2].xy, R0.wzzw;
  MUL result.texcoord[3].xyz, R0.x, R1.xzyw;
  MOV result.fogcoord.x, R2;
  MOV result.texcoord[0].w, R1;
  END
  # 21 instructions, 3 R-regs
  	"
}

}
Program "" {
SubProgram {
  Local 0, ([_BumpPeturb],0,0,0)
  Local 1, [_Color]

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

MAD R0.xyzw, R0, c[0].xxxy, fragment.texcoord[0];	# uv = _BumpAmt * totalbump + uv

TEX R1, R1, texture[3], 2D;		# lookup water color & reflection strength

TXP R0, R0, texture[0], RECT;	# lookup reflection
LRP result.color.rgb, R1.a, R0, R1;
MUL result.color.a, R0.a, R1.a;
END
  	"
}}

			SetTexture [_ReflectionTex] { combine texture }
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
  Local 5, ([_bScale],0,0,0)
  Local 6, [BumpParm]
  Local 7, [_Time]
  Local 9, [_ObjectSpaceCameraPos]

  "!!ARBvp1.0
  PARAM c[10] = { { 0, 0.5, -4, 4 },
  		state.matrix.mvp,
  		program.local[5..7],
  		{ 0.40000001, 0.5, 1 },
  		program.local[9] };
  TEMP R0;
  TEMP R1;
  TEMP R2;
  DP4 R2.xy, vertex.attrib[0], c[3];
  DP4 R1.w, vertex.attrib[0], c[4];
  MOV R0.z, R2.y;
  MOV R0.w, R1;
  DP4 R0.x, vertex.attrib[0], c[1];
  DP4 R0.y, vertex.attrib[0], c[2];
  MOV R1.x, c[7];
  MOV result.position, R0;
  DP4 result.texcoord[0].z, R0, c[0].xxyy;
  DP4 result.texcoord[0].y, R0, c[0].xzxw;
  DP4 result.texcoord[0].x, R0, c[0].wxxw;
  MUL R0, c[6], R1.x;
  MAD R0, vertex.attrib[0].xzxz, c[5].x, R0;
  ADD R1.xyz, -vertex.attrib[0], c[9];
  DP3 R2.y, R1, R1;
  MUL result.texcoord[1], R0, c[8].xyzz;
  RSQ R0.x, R2.y;
  MOV result.texcoord[2].xy, R0.wzzw;
  MUL result.texcoord[3].xyz, R0.x, R1.xzyw;
  MOV result.fogcoord.x, R2;
  MOV result.texcoord[0].w, R1;
  END
  # 21 instructions, 3 R-regs
  	"
}

}

Program "" {
SubProgram {
  Local 0, ([_BumpPeturb2],0,0,0)
  Local 1, [_Color]

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
	
	MAD r0.rg, r2, c0.r, r0;		# uv += totalbump

	MOV r0.b, c2.b;				# use perspective divide to scale refmap up to size
	
EndPass;

StartOutputPass;
	SampleMap r0, r0.str_dr;
 	SampleMap r3, r3.str;

	LERP r0.rgb, r3.a, r0, r3;	# 	Fade in reflection
	MUL r0.a, r0.a, r3.a;		# Make glossed reflections glow
EndPass;
" 
}
}
			SetTexture [_ReflectionTex] { combine texture }
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
			SetTexture [_ReflectionTex] { 
				combine texture lerp (previous) previous, previous * texture DOUBLE
				Matrix [_RefTex]
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
			SetTexture [_ReflectionTex] { 
				combine texture 
				Matrix [_RefTex]
			}
      		}
	}
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
