// Glass with fresnel reflection & transparency...
// Tested on: ATI Radeon Mobility

SHADER "Liquids/NonReflective wavy waterplane" { 
	Properties {
		_Color ("Water color", COLOR)  = ( .172 , .463 , .435 , 1)
		_horizonColor ("horizon color", COLOR)  = ( .172 , .463 , .435 , 1)
		_bScale ("Bump scale", Range (0,1)) = .5
		_bTwirl ("Bump Twirl", Range (0,.05)) = .5
		_BumpPeturb ("Bump strength", Range (0,256)) = .5
		_BumpPeturb2 ("Bump strength2", Range (0,1)) = 1
		_MainTex ("Main texture", 2D) = ""
		_ColorControl ("Color ramp (RGB) fresnel (A) ", 2D) = ""
		_BumpMap ("Bumpmap (RGB) ", 2D) = ""
	}  


Program "watery" {
SubProgram {
  Properties {
    BumpParm ("Bump (Scale, twirl, x speed, y speed)", vector) = (1,1,1,1)
    uvParams ("Uv scale, Uv pertubation, normal bending.", vector) = ( 10, .02, .03,0)
    waveDirY ("Waves Y dir + length", vector) = (0.0, 1.5, -7, 1)
    waveDirX ("Waves X dir + length", vector) = (-2.5, 0.0, 7, 8)
    waveHeights ("Waves heights", vector) = (.8, 1, .1, .05)
  }
  bind "vertex", ATTR0
  bind "normal", ATTR1
  bind "texcoord", ATTR2
  Local 11, [_ObjectSpaceCameraPos]
  Local 57, [BumpParm]
  Local 6, [_Time]
  Local 59, ([_bTwirl],0,0,0)
  Local 58, ([_bScale],0,0,0)
  Local 4, [uvParams]
  Local 3, [waveDirY]
  Local 2, [waveDirX]
  Local 1, [_waveTime]
  Local 0, [waveHeights]

  "!!ARBvp1.0
  PARAM c63 = { 0, 0, 0, 0 };
  PARAM c65 = { 1, -0.161616, 0.0083333, -0.00019841 };
  PARAM c66 = { -0.5, 0.0416667, -0.00138889, 2.48016e-05 };
  PARAM c67 = { 0, 1, 0, 0 };
  PARAM c68 = { 0.4, 0.5, 1, 1 };
  PARAM c64 = { 1.02, 0.5, 6.28319, 0 };
  TEMP R0, R1, R2, R3, R4, R5, R6, R7, R8, R9, R10;
  ATTRIB v2 = vertex.attrib[2];
  ATTRIB v1 = vertex.attrib[1];
  ATTRIB v0 = vertex.attrib[0];
  PARAM c11 = program.local[11];
  PARAM c57 = program.local[57];
  PARAM c6 = program.local[6];
  PARAM c59 = program.local[59];
  PARAM c58 = program.local[58];
  PARAM s259[4] = { state.matrix.mvp };
  PARAM c4 = program.local[4];
  PARAM c3 = program.local[3];
  PARAM c2 = program.local[2];
  PARAM c1 = program.local[1];
  PARAM c0 = program.local[0];
  	MOV result.color.front.primary, v2.y;
  	MOV R6, v0;
  	MUL R0, R6.z, c3;
  	MAD R0, R6.x, c2, R0;
  	ADD R0, c1, R0;
  	FRC R0, R0;
  	MOV R5.xyz, c64;
  	MAD R0, R0, R5.x, -R5.y;
  	MUL R4, R0, R5.z;
  	MUL R0, R4, R4;
  	MUL R3, R0, R4;
  	MUL R10, R3, R4;
  	MUL R2, R10, R4;
  	MUL R9, R2, R4;
  	MUL R1, R9, R4;
  	MUL R8, R1, R4;
  	MAD R0, R0, -R5.y, c65.x;
  	MAD R0, R10, c66.y, R0;
  	MAD R0, R9, c66.z, R0;
  	MAD R8, R8, c66.w, R0;
  	MUL R0, c0, v2.x;
  	MUL R9, R8, R0;
  	DP4 R8.x, R9, c2;
  	DP4 R8.y, R9, c3;
  	MAD R9.xyw, R8.xyxx, c4.z, v1.xzxx;
  	MOV R8.y, v1;
  	MOV R8.xz, R9.xyyw;
  	DP3 R5.w, R8.xyzx, R8.xyzx;
  	RSQ R5.w, R5.w;
  	MUL result.texcoord[0].xyz, R5.w, R8.xyzx;
  	MAD R3, R3, c65.y, R4;
  	MAD R2, R2, c65.z, R3;
  	MAD R1, R1, c65.w, R2;
  	DP4 R0.x, R1, R0;
  	MAD R2, v1.xyzx, R0.x, R6.xyzx;
  	MOV R6.xyz, R2;
  	DP4 R0.x, s259[0], R6;
  	DP4 R0.y, s259[1], R6;
  	DP4 R0.z, s259[2], R6;
  	DP4 R0.w, s259[3], R6;
  	MOV result.fogcoord.x, R0.z;
  	MOV result.position, R0;
  	MUL R0, R1.xyxy, c59.x;
  	MAD R1, R2.xzxz, c58.x, R0;
  	MOV R0.x, c6;
  	MAD R0, R0.x, c57, R1;
  	MUL result.texcoord[1], R0, c68;
  	ADD R0.yzw, c11.xxyz, -R2.xxyz;
  	DP3 R0.x, R0.yzwy, R0.yzwy;
  	RSQ R0.x, R0.x;
  	MUL R0.xyz, R0.x, R0.yzwy;
  	MAD R0, R0.xyzx, R5.y, R5.y;
  	MOV result.texcoord[2], R0.xzyw;
  	MOV result.texcoord[3], R7;
  END
  	"
}

}

Program "LowEndWatery" {
SubProgram {
  Properties {
    BumpParm ("Bump (Scale, twirl, x speed, y speed)", vector) = (1,1,1,1)
    uvParams ("Uv scale, Uv pertubation, normal bending.", vector) = ( 10, .02, .03,0)
    waveDirY ("Waves Y dir + length", vector) = (0.0, 1.5, -7, 1)
    waveDirX ("Waves X dir + length", vector) = (-2.5, 0.0, 7, 8)
    waveHeights ("Waves heights", vector) = (.8, 1, .1, .05)
  }
  bind "vertex", ATTR0
  bind "normal", ATTR1
  bind "texcoord", ATTR2
  Local 11, [_ObjectSpaceCameraPos]
  Local 57, [BumpParm]
  Local 6, [_Time]
  Local 59, ([_bTwirl],0,0,0)
  Local 58, ([_bScale],0,0,0)
  Local 4, [uvParams]
  Local 3, [waveDirY]
  Local 2, [waveDirX]
  Local 1, [_waveTime]
  Local 0, [waveHeights]

  "!!ARBvp1.0
  PARAM c61 = { 0, 0, 0, 0 };
  PARAM c63 = { 1, -0.161616, 0.0083333, -0.00019841 };
  PARAM c64 = { -0.5, 0.0416667, -0.00138889, 2.48016e-05 };
  PARAM c65 = { 0, 1, 0, 0 };
  PARAM c66 = { 0.4, 0.5, 0, 0 };
  PARAM c62 = { 1.02, 0.5, 6.28319, 0 };
  TEMP R0, R1, R2, R3, R4, R5, R6;
  ATTRIB v2 = vertex.attrib[2];
  ATTRIB v1 = vertex.attrib[1];
  ATTRIB v0 = vertex.attrib[0];
  PARAM c11 = program.local[11];
  PARAM c57 = program.local[57];
  PARAM c6 = program.local[6];
  PARAM c59 = program.local[59];
  PARAM c58 = program.local[58];
  PARAM s259[4] = { state.matrix.mvp };
  PARAM c4 = program.local[4];
  PARAM c3 = program.local[3];
  PARAM c2 = program.local[2];
  PARAM c1 = program.local[1];
  PARAM c0 = program.local[0];
  	MOV result.color.front.primary, v2.y;
  	MOV R0, v0;
  	MUL R2, R0.z, c3;
  	MAD R2, R0.x, c2, R2;
  	ADD R2, c1, R2;
  	FRC R2, R2;
  	MAD R2, R2, c62.x, -c62.y;
  	MUL R6, R2, c62.z;
  	MUL R2, R6, R6;
  	MUL R5, R2, R6;
  	MUL R2, R5, R6;
  	MUL R4, R2, R6;
  	MUL R2, R4, R6;
  	MUL R3, R2, R6;
  	MAD R2, R5, c63.y, R6;
  	MAD R2, R4, c63.z, R2;
  	MAD R4, R3, c63.w, R2;
  	MUL R2, c0, v2.x;
  	DP4 R2.x, R4, R2;
  	MAD R3, v1.xyzx, R2.x, R0.xyzx;
  	MOV R0.xyz, R3;
  	DP4 R2.x, s259[0], R0;
  	DP4 R2.y, s259[1], R0;
  	DP4 R2.z, s259[2], R0;
  	DP4 R2.w, s259[3], R0;
  	MOV result.fogcoord.x, R2.z;
  	MOV result.position, R2;
  	MUL R0, R4.xyxy, c59.x;
  	MAD R2, R3.xzxz, c58.x, R0;
  	MOV R0.x, c6;
  	MAD R2, R0.x, c57, R2;
  	MOV R0, c66;
  	MAD result.texcoord[1], R2, R0, c65.xxxy;
  	ADD R0.yzw, c11.xxyz, -R3.xxyz;
  	DP3 R0.x, R0.yzwy, R0.yzwy;
  	RSQ R0.x, R0.x;
  	MUL R0.y, R0.x, R0.yzwy;
  	MOV result.texcoord[0].xyz, R0.y;
  	MOV result.texcoord[0].w, c63.x;
  	MOV result.texcoord[2], R1;
  END
  	"
}

}

Program "SuckyWatery" {
SubProgram {
  Properties {
    horizonColor ("Water color at horizon", color) = (0.615,0.796,0.876,1)
    BumpParm ("Bump (Scale, twirl, x speed, y speed)", vector) = (1,1,1,1)
    uvParams ("Uv scale, Uv pertubation, normal bending.", vector) = ( 10, .02, .03,0)
    waveDirY ("Waves Y dir + length", vector) = (0.0, 1.5, -7, 1)
    waveDirX ("Waves X dir + length", vector) = (-2.5, 0.0, 7, 8)
    waveHeights ("Waves heights", vector) = (.8, 1, .1, .05)
  }
  bind "vertex", ATTR0
  bind "normal", ATTR1
  bind "texcoord", ATTR2
  Local 5, [horizonColor]
  Local 60, [_Color]
  Local 11, [_ObjectSpaceCameraPos]
  Local 57, [BumpParm]
  Local 6, [_Time]
  Local 59, ([_bTwirl],0,0,0)
  Local 58, ([_bScale],0,0,0)
  Local 4, [uvParams]
  Local 3, [waveDirY]
  Local 2, [waveDirX]
  Local 1, [_waveTime]
  Local 0, [waveHeights]

  "!!ARBvp1.0
  PARAM c61 = { 0, 0, 0, 0 };
  PARAM c63 = { 1, -0.161616, 0.0083333, -0.00019841 };
  PARAM c64 = { -0.5, 0.0416667, -0.00138889, 2.48016e-05 };
  PARAM c65 = { 0, 1, 0, 0 };
  PARAM c66 = { 0.4, 0.5, 0, 0 };
  PARAM c67 = { 128, 128, 0, 0 };
  PARAM c62 = { 1.02, 0.5, 6.28319, 256 };
  TEMP R0, R1, R2, R3, R4, R5;
  ATTRIB v2 = vertex.attrib[2];
  ATTRIB v1 = vertex.attrib[1];
  ATTRIB v0 = vertex.attrib[0];
  PARAM c5 = program.local[5];
  PARAM c60 = program.local[60];
  PARAM c11 = program.local[11];
  PARAM c57 = program.local[57];
  PARAM c6 = program.local[6];
  PARAM c59 = program.local[59];
  PARAM c58 = program.local[58];
  PARAM s259[4] = { state.matrix.mvp };
  PARAM c4 = program.local[4];
  PARAM c3 = program.local[3];
  PARAM c2 = program.local[2];
  PARAM c1 = program.local[1];
  PARAM c0 = program.local[0];
  	MOV R0, v0;
  	MUL R1, R0.z, c3;
  	MAD R1, R0.x, c2, R1;
  	ADD R1, c1, R1;
  	FRC R1, R1;
  	MAD R1, R1, c62.x, -c62.y;
  	MUL R5, R1, c62.z;
  	MUL R1, R5, R5;
  	MUL R4, R1, R5;
  	MUL R1, R4, R5;
  	MUL R3, R1, R5;
  	MUL R1, R3, R5;
  	MUL R2, R1, R5;
  	MAD R1, R4, c63.y, R5;
  	MAD R1, R3, c63.z, R1;
  	MAD R4, R2, c63.w, R1;
  	MUL R1, c0, v2.x;
  	DP4 R1.x, R4, R1;
  	MAD R3, v1.xyzx, R1.x, R0.xyzx;
  	MOV R0.xyz, R3;
  	DP4 R2.x, s259[0], R0;
  	DP4 R2.y, s259[1], R0;
  	DP4 R2.z, s259[2], R0;
  	DP4 R2.w, s259[3], R0;
  	MOV result.fogcoord.x, R2.z;
  	MOV result.position, R2;
  	MUL R0, R4.xyxy, c59.x;
  	MAD R1, R3.xzxz, c58.x, R0;
  	MOV R0.x, c6;
  	MAD R1, R0.x, c57, R1;
  	MOV R0, c66;
  	MAD result.texcoord[0], R1, R0, c65.xxxy;
  	RCP R0.x, R2.w;
  	MUL R1.xy, R2.xyxx, R0.x;
  	MAD R1.xy, R1.xyxx, c67.xyxx, c67.x;
  	MOV result.texcoord[1].x, R1.x;
  	ADD result.texcoord[1].y, c62.w, -R1.y;
  	ADD R0.yzw, c11.xxyz, -R3.xxyz;
  	DP3 R0.x, R0.yzwy, R0.yzwy;
  	RSQ R0.x, R0.x;
  	MUL R0.y, R0.x, R0.yzwy;
  	ADD R0.x, c63.x, -R0.y;
  	MUL R0.x, R0.x, R0.x;
  	MUL R2.x, R0.x, R0.x;
  	MOV R1, c60;
  	ADD R0, c5, -R1;
  	MAD R0, R2.x, R0, R1;
  	MOV result.color.front.primary.xyz, R0;
  	MUL result.color.front.primary.w, R0.w, v2.y;
  END
  	"
}

}

	//  ------------------------------------------------------------
	// Radeon 9000
	//  ------------------------------------------------------------
	SUBSHADER { 
		Tags { "Queue" = "Transparent" }
Program "" {
SubProgram {
  Properties {
    BumpParm ("Bump (Scale, twirl, x speed, y speed)", vector) = (1,1,1,1)
    uvParams ("Uv scale, Uv pertubation, normal bending.", vector) = ( 10, .02, .03,0)
    waveDirY ("Waves Y dir + length", vector) = (0.0, 1.5, -7, 1)
    waveDirX ("Waves X dir + length", vector) = (-2.5, 0.0, 7, 8)
    waveHeights ("Waves heights", vector) = (.8, 1, .1, .05)
  }
  bind "vertex", ATTR0
  bind "normal", ATTR1
  bind "texcoord", ATTR2
  Local 11, [_ObjectSpaceCameraPos]
  Local 57, [BumpParm]
  Local 6, [_Time]
  Local 58, ([_bScale],0,0,0)
  Local 4, [uvParams]
  Local 3, [waveDirY]
  Local 2, [waveDirX]
  Local 1, [_waveTime]
  Local 0, [waveHeights]

  "!!ARBvp1.0
  PARAM c61 = { 0, 0, 0, 0 };
  PARAM c63 = { 1, -0.161616, 0.0083333, -0.00019841 };
  PARAM c64 = { -0.5, 0.0416667, -0.00138889, 2.48016e-05 };
  PARAM c65 = { 0.4, 0.5, 1, 1 };
  PARAM c66 = { 4, 0, 0, 4 };
  PARAM c67 = { 0, -4, 0, 4 };
  PARAM c62 = { 1.02, 0.5, 6.28319, 2 };
  PARAM c68 = { 0, 0, 0.5, 0.5 };
  PARAM c70 = { 0, 0, 0, 1 };
  PARAM c69 = { 3, 0, 0, 0 };
  TEMP R0, R1, R2, R3, R4, R5;
  ATTRIB v2 = vertex.attrib[2];
  ATTRIB v1 = vertex.attrib[1];
  ATTRIB v0 = vertex.attrib[0];
  PARAM c11 = program.local[11];
  PARAM c57 = program.local[57];
  PARAM c6 = program.local[6];
  PARAM c58 = program.local[58];
  PARAM s259[4] = { state.matrix.mvp };
  PARAM c4 = program.local[4];
  PARAM c3 = program.local[3];
  PARAM c2 = program.local[2];
  PARAM c1 = program.local[1];
  PARAM c0 = program.local[0];
  	MOV result.color.front.primary, v2.y;
  	MOV R0, v0;
  	MUL R1, R0.z, c3;
  	MAD R1, R0.x, c2, R1;
  	ADD R1, c1, R1;
  	FRC R1, R1;
  	MAD R1, R1, c62.x, -c62.y;
  	MUL R5, R1, c62.z;
  	MUL R1, R5, R5;
  	MUL R4, R1, R5;
  	MUL R1, R4, R5;
  	MUL R3, R1, R5;
  	MUL R1, R3, R5;
  	MUL R2, R1, R5;
  	MAD R1, R4, c63.y, R5;
  	MAD R1, R3, c63.z, R1;
  	MAD R2, R2, c63.w, R1;
  	MUL R1, c0, v2.x;
  	DP4 R1.x, R2, R1;
  	MAD R2, v1.xyzx, R1.x, R0.xyzx;
  	MOV R0.xyz, R2;
  	DP4 R1.x, s259[0], R0;
  	DP4 R1.y, s259[1], R0;
  	DP4 R1.z, s259[2], R0;
  	DP4 R1.w, s259[3], R0;
  	MOV result.fogcoord.x, R1.z;
  	MOV result.position, R1;
  	MOV R0.x, c6;
  	MUL R0, R0.x, c57;
  	MAD R0, R2.xzxz, c58.x, R0;
  	MOV result.texcoord[2], R0.wzww;
  	MUL result.texcoord[1], R0, c65;
  	DP4 result.texcoord[0].x, c66.xyyx, R1;
  	DP4 result.texcoord[0].y, c67.xyxw, R1;
  	DP4 result.texcoord[0].z, c68.xxzz, R1;
  	MOV result.texcoord[0].w, R1.w;
  	ADD R0.yzw, c11.xxyz, -R2.xxyz;
  	DP3 R0.x, R0.yzwy, R0.yzwy;
  	RSQ R0.x, R0.x;
  	MUL R0, R0.x, R0.yzwy;
  	MOV result.texcoord[3], R0.xzyw;
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
	PassTexCoord r4, t4.str;
	# r0.rg = Reflection coord
	ADD r2, r1.bias, r2.bias;		# totalbump = bump1 + bump2

	DOT3 r3, r2, r3;				# r4.a = fresnel  [ dot (totalbump, viewer-pos)
EndPass;

StartOutputPass;
 	SampleMap r3, r3.str;
	LERP r0.rgb, r3.a, c1, r3;	# 	Fade in reflection
	MOV r0.a, color0.a;
EndPass;
" 
}
}

		Blend SrcAlpha OneMinusSrcAlpha
		ColorMask RGB
//		ZWrite Off
		Pass { 
			SetTexture [_ReflectionTex] { combine texture }
			SetTexture [_BumpMap] {combine texture, previous alpha * texture alpha  }
			SetTexture [_BumpMap] {combine texture, previous alpha * texture alpha  }
			SetTexture [_ColorControl] {combine texture, previous alpha * texture alpha  }
			SetTexture [_ColorControl] {combine texture, previous alpha * texture alpha  }
    		}
	}

	//  ------------------------------------------------------------
	// GeforceMX
	//  ------------------------------------------------------------
	SUBSHADER { 
		Tags { "Queue" = "Transparent" }
		BindProgram "SuckyWatery"
		Blend SrcAlpha OneMinusSrcAlpha
		ColorMask RGB
//		ZWrite Off
		Pass { 
			SetTexture [_BumpMap] {
				combine previous, previous +- texture DOUBLE
			}
			SetTexture [_BumpMap] { 
				constantColor [_horizonColor]
				combine constant lerp (previous) previous, previous DOUBLE
			}
      		}
	}

	// NON-VP 

	SUBSHADER {
		Tags { "Queue" = "Transparent" }
		Blend SrcAlpha OneMinusSrcAlpha
		ColorMask RGB
//		ZWrite Off
		Pass { 
			SetTexture [_MainTex] {combine texture, primary * texture alpha  }
      		}
	}

}

