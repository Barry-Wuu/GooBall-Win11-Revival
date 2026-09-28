// Glass with fresnel reflection & transparency...
// Tested on: ATI Radeon Mobility

SHADER "Liquids/Reflective wavy waterplane" { 
	Properties {
		_Color ("Water color", COLOR)  = ( .172 , .463 , .435 , 1)
		_horizonColor ("horizon color", COLOR)  = ( .172 , .463 , .435 , 1)
		_bScale ("Bump scale", Range (0,1)) = .5
		_bTwirl ("Bump Twirl", Range (0,.05)) = .5
		_BumpPeturb ("Bump strength", Range (0,256)) = .5
		_BumpPeturb2 ("Bump strength2", Range (0,1)) = 1
		_MainTex ("Main texture", 2D) = ""
		_ReflectionTex ("Environment Reflection", RECT) = "spheremap.jpg"
		_ColorControl ("Color ramp (RGB) fresnel (A) ", 2D) = ""
		_BumpMap ("Bumpmap (RGB) ", 2D) = ""
	}  


Program "watery" {
SubProgram {
  Properties {
    waveDirX ("Waves X dir + length", vector) = (-2.5, 0.0, 7, 8)
    waveDirY ("Waves Y dir + length", vector) = (0.0, 1.5, -7, 1)
    waveHeights ("Waves heights", vector) = (.8, 1, .1, .05)
    uvParams ("Uv scale, Uv pertubation, normal bending.", vector) = ( 10, .02, .03,0)
    BumpParm ("Bump (Scale, twirl, x speed, y speed)", vector) = (1,1,1,1)
  }
  bind "vertex", ATTR0
  bind "normal", ATTR1
  bind "texcoord", ATTR2
  Local 5, [waveDirX]
  Local 6, [waveDirY]
  Local 7, [_waveTime]
  Local 9, [waveHeights]
  Local 11, [uvParams]
  Local 12, [BumpParm]
  Local 13, [_Time]
  Local 14, ([_bScale],0,0,0)
  Local 15, ([_bTwirl],0,0,0)
  Local 18, [_ObjectSpaceCameraPos]

  "!!ARBvp1.0
  PARAM c[19] = { { 1.02, 0.5, 6.2831855, -0.00019840999 },
  		state.matrix.mvp,
  		program.local[5..7],
  		{ 0.0083333002, -0.16161616, 2.4801588e-05, -0.0013888889 },
  		program.local[9],
  		{ -0.5, 0.041666664, 1 },
  		program.local[11..15],
  		{ 0.40000001, 0.5, 1 },
  		{ 128, 64 },
  		program.local[18] };
  TEMP R0;
  TEMP R1;
  TEMP R2;
  TEMP R3;
  TEMP R4;
  TEMP R5;
  MUL R0, vertex.attrib[0].z, c[6];
  MAD R0, vertex.attrib[0].x, c[5], R0;
  ADD R0, R0, c[7];
  FRC R0, R0;
  MUL R0, R0, c[0].x;
  ADD R0, R0, -c[0].y;
  MUL R0, R0, c[0].z;
  MUL R1, R0, R0;
  MUL R2, R1, R0;
  MUL R4, R2, R0;
  MUL R5, R4, c[10].y;
  MUL R3, R4, R0;
  MUL R4, R3, R0;
  MAD R5, R1, c[10].x, R5;
  MUL R1, R4, R0;
  MAD R5, R4, c[8].w, R5;
  MUL R4, R1, R0;
  MAD R0, R2, c[8].y, R0;
  MAD R0, R3, c[8].x, R0;
  MAD R4, R4, c[8].z, R5;
  MAD R0, R1, c[0].w, R0;
  MUL R3, vertex.attrib[2].x, c[9];
  DP4 R0.z, R0, R3;
  ADD R2, R4, c[10].z;
  MUL R2, R2, R3;
  MUL R1.xyz, vertex.attrib[1], R0.z;
  ADD R3.xyz, R1, vertex.attrib[0];
  MOV R3.w, vertex.attrib[0];
  DP4 R4.xy, R3, c[3];
  DP4 R4.zw, R3, c[4];
  DP4 R0.w, R2, c[6];
  DP4 R0.z, R2, c[5];
  MAD R2.xz, R0.zyww, c[11].z, vertex.attrib[1];
  MUL R0, R0.xyxy, c[15].x;
  MOV R1.w, R4;
  MOV R1.z, R4.y;
  DP4 R1.x, R3, c[1];
  DP4 R1.y, R3, c[2];
  MOV result.position, R1;
  MOV R2.y, vertex.attrib[1];
  DP3 R1.z, R2, R2;
  RSQ R1.z, R1.z;
  MUL result.texcoord[0].xyz, R1.z, R2;
  RCP R1.z, R4.z;
  MUL R1.xy, R1, R1.z;
  MUL R1.xy, R1, c[17];
  MAD R0, R3.xzxz, c[14].x, R0;
  MOV R1.w, c[13].x;
  MAD R0, c[12], R1.w, R0;
  MUL result.texcoord[1], R0, c[16].xyzz;
  ADD R0.xyz, -R3, c[18];
  DP3 R0.w, R0, R0;
  RSQ R0.w, R0.w;
  MUL R0.xyz, R0.w, R0;
  ADD result.texcoord[2].xy, R1, c[17];
  MAD result.texcoord[3].xyz, R0.xzyw, c[0].y, c[0].y;
  MOV result.fogcoord.x, R4;
  MOV result.color.w, vertex.attrib[2].y;
  END
  # 58 instructions, 6 R-regs
  	"
}

}

Program "LowEndWatery" {
SubProgram {
  Properties {
    waveDirX ("Waves X dir + length", vector) = (-2.5, 0.0, 7, 8)
    waveDirY ("Waves Y dir + length", vector) = (0.0, 1.5, -7, 1)
    waveHeights ("Waves heights", vector) = (.8, 1, .1, .05)
    BumpParm ("Bump (Scale, twirl, x speed, y speed)", vector) = (1,1,1,1)
  }
  bind "vertex", ATTR0
  bind "normal", ATTR1
  bind "texcoord", ATTR2
  Local 5, [waveDirX]
  Local 6, [waveDirY]
  Local 7, [_waveTime]
  Local 9, [waveHeights]
  Local 10, [_ObjectSpaceCameraPos]
  Local 11, [BumpParm]
  Local 12, [_Time]
  Local 13, ([_bScale],0,0,0)
  Local 14, ([_bTwirl],0,0,0)

  "!!ARBvp1.0
  PARAM c[16] = { { 1.02, 0.5, 6.2831855, -0.00019840999 },
  		state.matrix.mvp,
  		program.local[5..7],
  		{ 0.0083333002, -0.16161616, 1, 0 },
  		program.local[9..14],
  		{ 0.40000001, 0.5, 0, 128 } };
  TEMP R0;
  TEMP R1;
  TEMP R2;
  TEMP R3;
  MUL R0, vertex.attrib[0].z, c[6];
  MAD R0, vertex.attrib[0].x, c[5], R0;
  ADD R0, R0, c[7];
  FRC R0, R0;
  MUL R0, R0, c[0].x;
  ADD R0, R0, -c[0].y;
  MUL R0, R0, c[0].z;
  MUL R1, R0, R0;
  MUL R2, R1, R0;
  MUL R1, R2, R0;
  MAD R3, R2, c[8].y, R0;
  MUL R1, R1, R0;
  MUL R2, R1, R0;
  MUL R0, R2, R0;
  MAD R1, R1, c[8].x, R3;
  MAD R0, R0, c[0].w, R1;
  MUL R2, vertex.attrib[2].x, c[9];
  DP4 R0.z, R0, R2;
  MUL R1.xyz, vertex.attrib[1], R0.z;
  ADD R2.xyz, R1, vertex.attrib[0];
  MOV R2.w, vertex.attrib[0];
  DP4 R3.xy, R2, c[3];
  MUL R0, R0.xyxy, c[14].x;
  MOV R1.x, c[12];
  MAD R0, R2.xzxz, c[13].x, R0;
  MAD R0, c[11], R1.x, R0;
  MUL R1, R0, c[15].xyzz;
  DP4 R3.zw, R2, c[4];
  ADD result.texcoord[1], R1, c[8].wwwz;
  MOV R0.w, R3;
  MOV R0.z, R3.y;
  DP4 R0.x, R2, c[1];
  DP4 R0.y, R2, c[2];
  MOV result.position, R0;
  ADD R1.xyz, -R2, c[10];
  RCP R0.z, R3.z;
  MUL R0.xy, R0, R0.z;
  DP3 R0.w, R1, R1;
  RSQ R0.z, R0.w;
  MAD result.texcoord[2].xy, R0, c[15].w, c[15].w;
  MUL result.texcoord[0].xyz, R0.z, R1.y;
  MOV result.fogcoord.x, R3;
  MOV result.color.w, vertex.attrib[2].y;
  MOV result.texcoord[0].w, c[8].z;
  END
  # 44 instructions, 4 R-regs
  	"
}

}

Program "SuckyWatery" {
SubProgram {
  Properties {
    waveDirX ("Waves X dir + length", vector) = (-2.5, 0.0, 7, 8)
    waveDirY ("Waves Y dir + length", vector) = (0.0, 1.5, -7, 1)
    waveHeights ("Waves heights", vector) = (.8, 1, .1, .05)
    horizonColor ("Water color at horizon", color) = (0.615,0.796,0.876,1)
    BumpParm ("Bump (Scale, twirl, x speed, y speed)", vector) = (1,1,1,1)
  }
  bind "vertex", ATTR0
  bind "normal", ATTR1
  bind "texcoord", ATTR2
  Local 5, [waveDirX]
  Local 6, [waveDirY]
  Local 7, [_waveTime]
  Local 9, [waveHeights]
  Local 10, [_ObjectSpaceCameraPos]
  Local 11, [_Color]
  Local 12, [horizonColor]
  Local 13, [BumpParm]
  Local 14, [_Time]
  Local 15, ([_bScale],0,0,0)
  Local 16, ([_bTwirl],0,0,0)

  "!!ARBvp1.0
  PARAM c[18] = { { 1.02, 0.5, 6.2831855, -0.00019840999 },
  		state.matrix.mvp,
  		program.local[5..7],
  		{ 0.0083333002, -0.16161616, 1, 0 },
  		program.local[9..16],
  		{ 0.40000001, 0.5, 0, 128 } };
  TEMP R0;
  TEMP R1;
  TEMP R2;
  TEMP R3;
  MUL R0, vertex.attrib[0].z, c[6];
  MAD R0, vertex.attrib[0].x, c[5], R0;
  ADD R0, R0, c[7];
  FRC R0, R0;
  MUL R0, R0, c[0].x;
  ADD R0, R0, -c[0].y;
  MUL R0, R0, c[0].z;
  MUL R1, R0, R0;
  MUL R2, R1, R0;
  MUL R1, R2, R0;
  MAD R3, R2, c[8].y, R0;
  MUL R1, R1, R0;
  MUL R2, R1, R0;
  MUL R0, R2, R0;
  MAD R1, R1, c[8].x, R3;
  MAD R0, R0, c[0].w, R1;
  MUL R2, vertex.attrib[2].x, c[9];
  DP4 R0.z, R0, R2;
  MUL R1.xyz, vertex.attrib[1], R0.z;
  ADD R2.xyz, R1, vertex.attrib[0];
  MOV R2.w, vertex.attrib[0];
  DP4 R3.xy, R2, c[3];
  MUL R0, R0.xyxy, c[16].x;
  MAD R0, R2.xzxz, c[15].x, R0;
  MOV R1.x, c[14];
  MAD R1, c[13], R1.x, R0;
  MUL R1, R1, c[17].xyzz;
  DP4 R3.zw, R2, c[4];
  DP4 R0.x, R2, c[1];
  DP4 R0.y, R2, c[2];
  MOV R0.w, R3;
  MOV R0.z, R3.y;
  MOV result.position, R0;
  ADD R2.xyz, -R2, c[10];
  DP3 R0.z, R2, R2;
  ADD result.texcoord[0], R1, c[8].wwwz;
  RCP R0.w, R3.z;
  RSQ R0.z, R0.z;
  MUL R1.xy, R0, R0.w;
  MAD R1.z, -R0, R2.y, c[8];
  MOV R0, c[12];
  MUL R1.z, R1, R1;
  ADD R0, -c[11], R0;
  MUL R1.z, R1, R1;
  MAD R0, R1.z, R0, c[11];
  MAD result.texcoord[1].xy, R1, c[17].w, c[17].w;
  MUL result.color.w, R0, vertex.attrib[2].y;
  MOV result.color.xyz, R0;
  MOV result.fogcoord.x, R3;
  END
  # 49 instructions, 4 R-regs
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
    waveDirX ("Waves X dir + length", vector) = (-2.5, 0.0, 7, 8)
    waveDirY ("Waves Y dir + length", vector) = (0.0, 1.5, -7, 1)
    waveHeights ("Waves heights", vector) = (.8, 1, .1, .05)
    BumpParm ("Bump (Scale, twirl, x speed, y speed)", vector) = (1,1,1,1)
  }
  bind "vertex", ATTR0
  bind "normal", ATTR1
  bind "texcoord", ATTR2
  Local 5, [waveDirX]
  Local 6, [waveDirY]
  Local 7, [_waveTime]
  Local 9, [waveHeights]
  Local 11, ([_bScale],0,0,0)
  Local 12, [BumpParm]
  Local 13, [_Time]
  Local 15, [_ObjectSpaceCameraPos]

  "!!ARBvp1.0
  PARAM c[16] = { { 1.02, 0.5, 6.2831855, -0.00019840999 },
  		state.matrix.mvp,
  		program.local[5..7],
  		{ 0.0083333002, -0.16161616, 0, 0.5 },
  		program.local[9],
  		{ 0, 4 },
  		program.local[11..13],
  		{ 0.40000001, 0.5, 1 },
  		program.local[15] };
  TEMP R0;
  TEMP R1;
  TEMP R2;
  TEMP R3;
  MUL R0, vertex.attrib[0].z, c[6];
  MAD R0, vertex.attrib[0].x, c[5], R0;
  ADD R0, R0, c[7];
  FRC R0, R0;
  MUL R0, R0, c[0].x;
  ADD R0, R0, -c[0].y;
  MUL R0, R0, c[0].z;
  MUL R1, R0, R0;
  MUL R2, R1, R0;
  MUL R1, R2, R0;
  MUL R1, R1, R0;
  MAD R3, R2, c[8].y, R0;
  MUL R2, R1, R0;
  MUL R0, R2, R0;
  MAD R1, R1, c[8].x, R3;
  MAD R0, R0, c[0].w, R1;
  MUL R2, vertex.attrib[2].x, c[9];
  DP4 R0.x, R0, R2;
  MUL R0.xyz, vertex.attrib[1], R0.x;
  ADD R1.xyz, R0, vertex.attrib[0];
  MOV R1.w, vertex.attrib[0];
  DP4 R2.w, R1, c[4];
  DP4 R3.xy, R1, c[3];
  DP4 R0.x, R1, c[1];
  DP4 R0.y, R1, c[2];
  MOV R0.w, R2;
  MOV R0.z, R3.y;
  MOV result.position, R0;
  DP4 result.texcoord[0].z, R0, c[8].zzww;
  DP4 result.texcoord[0].y, R0, c[10].xyxy;
  DP4 result.texcoord[0].x, R0, c[10].yxxy;
  ADD R2.xyz, -R1, c[15];
  DP3 R0.y, R2, R2;
  RSQ R1.y, R0.y;
  MOV R0.x, c[13];
  MUL R0, c[12], R0.x;
  MAD R0, R1.xzxz, c[11].x, R0;
  MUL result.texcoord[3].xyz, R1.y, R2.xzyw;
  MOV result.texcoord[0].w, R2;
  MUL result.texcoord[1], R0, c[14].xyzz;
  MOV result.texcoord[2].xy, R0.wzzw;
  MOV result.fogcoord.x, R3;
  MOV result.color.w, vertex.attrib[2].y;
  END
  # 43 instructions, 4 R-regs
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
	PassTexCoord r4, t4.str;
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
	// ARB_FP
	//  ------------------------------------------------------------
	SUBSHADER { 
		Tags { "Queue" = "Transparent" }
Program "" {
SubProgram {
  Properties {
    waveDirX ("Waves X dir + length", vector) = (-2.5, 0.0, 7, 8)
    waveDirY ("Waves Y dir + length", vector) = (0.0, 1.5, -7, 1)
    waveHeights ("Waves heights", vector) = (.8, 1, .1, .05)
    BumpParm ("Bump (Scale, twirl, x speed, y speed)", vector) = (1,1,1,1)
  }
  bind "vertex", ATTR0
  bind "normal", ATTR1
  bind "texcoord", ATTR2
  Local 5, [waveDirX]
  Local 6, [waveDirY]
  Local 7, [_waveTime]
  Local 9, [waveHeights]
  Local 11, ([_bScale],0,0,0)
  Local 12, [BumpParm]
  Local 13, [_Time]
  Local 15, [_ObjectSpaceCameraPos]

  "!!ARBvp1.0
  PARAM c[16] = { { 1.02, 0.5, 6.2831855, -0.00019840999 },
  		state.matrix.mvp,
  		program.local[5..7],
  		{ 0.0083333002, -0.16161616, 0, 0.5 },
  		program.local[9],
  		{ 0, 128 },
  		program.local[11..13],
  		{ 0.40000001, 0.5, 1 },
  		program.local[15] };
  TEMP R0;
  TEMP R1;
  TEMP R2;
  TEMP R3;
  MUL R0, vertex.attrib[0].z, c[6];
  MAD R0, vertex.attrib[0].x, c[5], R0;
  ADD R0, R0, c[7];
  FRC R0, R0;
  MUL R0, R0, c[0].x;
  ADD R0, R0, -c[0].y;
  MUL R0, R0, c[0].z;
  MUL R1, R0, R0;
  MUL R2, R1, R0;
  MUL R1, R2, R0;
  MUL R1, R1, R0;
  MAD R3, R2, c[8].y, R0;
  MUL R2, R1, R0;
  MUL R0, R2, R0;
  MAD R1, R1, c[8].x, R3;
  MAD R0, R0, c[0].w, R1;
  MUL R2, vertex.attrib[2].x, c[9];
  DP4 R0.x, R0, R2;
  MUL R0.xyz, vertex.attrib[1], R0.x;
  ADD R1.xyz, R0, vertex.attrib[0];
  MOV R1.w, vertex.attrib[0];
  DP4 R2.w, R1, c[4];
  DP4 R3.xy, R1, c[3];
  DP4 R0.x, R1, c[1];
  DP4 R0.y, R1, c[2];
  MOV R0.w, R2;
  MOV R0.z, R3.y;
  MOV result.position, R0;
  DP4 result.texcoord[0].z, R0, c[8].zzww;
  DP4 result.texcoord[0].y, R0, c[10].xyxy;
  DP4 result.texcoord[0].x, R0, c[10].yxxy;
  ADD R2.xyz, -R1, c[15];
  DP3 R0.y, R2, R2;
  RSQ R1.y, R0.y;
  MOV R0.x, c[13];
  MUL R0, c[12], R0.x;
  MAD R0, R1.xzxz, c[11].x, R0;
  MUL result.texcoord[3].xyz, R1.y, R2.xzyw;
  MOV result.texcoord[0].w, R2;
  MUL result.texcoord[1], R0, c[14].xyzz;
  MOV result.texcoord[2].xy, R0.wzzw;
  MOV result.fogcoord.x, R3;
  MOV result.color.w, vertex.attrib[2].y;
  END
  # 43 instructions, 4 R-regs
  	"
}

}
Program "" {
SubProgram {
  Local 0, ([_BumpPeturb],0,0,0)
  Local 1, [_Color]

  "!!ARBfp1.0
OPTION ARB_precision_hint_fastest;
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
MAD result.color.a, R0.a, R1.a, fragment.color.a;
END
  	"
}}
		Blend SrcAlpha OneMinusSrcAlpha
		ColorMask RGB
//		ZWrite Off
		Pass { 
			SetTexture [_ReflectionTex] { combine texture }
			SetTexture [_BumpMap] {combine texture, previous alpha * texture alpha  }
			SetTexture [_BumpMap] {combine texture, previous alpha * texture alpha  }
			SetTexture [_ColorControl] {combine texture, previous alpha * texture alpha  }
      		}
	}

	//  ------------------------------------------------------------
	// R7k
	//  ------------------------------------------------------------
	SUBSHADER {
		Tags { "Queue" = "Transparent" }
		BindProgram "LowEndWatery"
		Blend SrcAlpha OneMinusSrcAlpha
		ColorMask RGB
//		ZWrite Off
		Pass { 
			SetTexture [_ColorControl] {combine texture, primary * texture alpha  }
			SetTexture [_BumpMap] {
				combine previous, previous +- texture
			}
			SetTexture [_ReflectionTex] { 
				constantColor (1,0,0,0)
				combine texture lerp (previous) previous, previous + texture DOUBLE
			}
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
			SetTexture [_ReflectionTex] { 
				constantColor (0,0,0, 1)
				combine texture lerp (previous) previous, previous * constant + texture
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
