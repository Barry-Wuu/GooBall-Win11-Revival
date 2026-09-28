Shader " Glossy" {
	Properties {
		_Color ("Main Color", Color) = (1,1,1,1)
		_SpecColor ("Specular Color", Color) = (0.5, 0.5, 0.5, 1)
		_Shininess ("Shininess", float) = 20
		_MainTex ("Base (RGB) Gloss (A)", 2D) = "ah64rotor1"
	}
	Category {
		tags { "lod" = "0" }
		// ---------------------------------------------------------
		// Geforce 3, ARB_FP
		// ---------------------------------------------------------
		SubShader {
			Lighting On
			TexCount 4		// Get Geforce2s to ignore this shader
			Pass {					// Ambient only
				Tags {"LightMode" = "PixelOrNone"}
				Blend AppSrcAdd AppDstAdd
				Color [_PPLAmbient]
				SetTexture [_MainTex] {constantColor [_Color] Combine texture * primary DOUBLE, texture *  constant}
			}
			Pass { 
				Tags {"LightMode" = "Vertex"} 
 				Blend AppSrcAdd AppDstAdd
				Material {
					Diffuse [_Color]
					Emission [_PPLAmbient]
				}
				Lighting On
				SetTexture [_MainTex] {constantColor [_PPLAmbent] Combine texture * primary DOUBLE,constant}
			}
			Pass {
				Tags {"LightMode" = "Vertex"}
				Blend One One
				Material {
					Specular [_SpecColor]
					Shininess [_Shininess]
				}
				Lighting On
				Fog { Color [_AddFog] }
				SetTexture [_MainTex] {Combine texture alpha* primary, constant}
			} 
			Pass {	
				// Sum all light contribs from 2-tex lights
				Tags { 
					"LightMode" = "Pixel" 
				}
				Blend AppSrcAdd AppDstAdd
				Fog { Color [_AddFog] }
				Material { Diffuse [_Color] }
				Color (1,1,1,1)
				Lighting On
Program "" {
SubProgram {
  Type 1
  Local 8, [_PPLAmbient]
  Local 17, [_PPLAmbient]
  Local 9, [_SpecColor]
  Local 16, [_SpecColor]
  SetTexture [_MainTex]
  SetTexture [_SpecCube0]

  "!!TS1.0
  texture_2d();
  texture_cube_map();
  !!RC1.0
  {
    rgb
    {
      col0 = col0.rgb * unsigned_invert(zero.rgb);
      scale_by_two();
    }
    alpha
    {
      col0 = tex1.a * tex0.a;
    }
  }
  {
    rgb
    {
      discard = col0.rgb * unsigned_invert(zero.rgb);
      discard = const0.rgb * unsigned_invert(zero.rgb);
      col0 = sum();
    }
    alpha
    {
      col1 = const1.a * col0.a;
      scale_by_two();
    }
  }
  {
    rgb
    {
      col1 = const0.rgb * col0.a;
      scale_by_two();
    }
    alpha
    {
      discard = col1.a * unsigned_invert(zero.a);
      discard = const1.a * tex0.a;
      col0 = sum();
    }
  }
  {
    rgb
    {
      discard = tex0.rgb * col0.rgb;
      discard = col1.rgb * unsigned_invert(zero.rgb);
      col0 = sum();
    }
  }
  out.rgb = unsigned(col0.rgb);
  out.a = unsigned(col0.a);
  // 7 instructions
  	"
}
SubProgram {
  Type 2
  Local 8, [_PPLAmbient]
  Local 24, [_PPLAmbient]
  Local 16, [_SpecColor]
  SetTexture [_MainTex]
  SetTexture [_SpecCube0]

  "!!TS1.0
  texture_2d();
  texture_cube_map();
  texture_2d();
  !!RC1.0
  {
    rgb
    {
      col0 = tex2.a * col0.rgb;
      scale_by_two();
    }
    alpha
    {
      col0 = tex2.a * tex1.a;
    }
  }
  {
    rgb
    {
      discard = col0.rgb * unsigned_invert(zero.rgb);
      discard = const0.rgb * unsigned_invert(zero.rgb);
      col0 = sum();
    }
    alpha
    {
      col0 = col0.a * tex0.a;
    }
  }
  {
    rgb
    {
      col1 = const0.rgb * col0.a;
      scale_by_two();
    }
    alpha
    {
      col0 = const0.a * col0.a;
      scale_by_two();
    }
  }
  {
    rgb
    {
      discard = tex0.rgb * col0.rgb;
      discard = col1.rgb * unsigned_invert(zero.rgb);
      col0 = sum();
    }
    alpha
    {
      discard = col0.a * unsigned_invert(zero.a);
      discard = const0.a * tex0.a;
      col0 = sum();
    }
  }
  out.rgb = unsigned(col0.rgb);
  out.a = unsigned(col0.a);
  // 8 instructions
  	"
}
SubProgram {
  Type 3
  Local 16, [_PPLAmbient]
  Local 32, [_PPLAmbient]
  Local 24, [_SpecColor]
  SetTexture [_MainTex]
  SetTexture [_SpecCube0]

  "!!TS1.0
  texture_2d();
  texture_cube_map();
  texture_2d();
  texture_2d();
  !!RC1.0
  {
    alpha
    {
      col0 = tex2.a * tex3.a;
    }
  }
  {
    rgb
    {
      col0 = col0.a * col0.rgb;
      scale_by_two();
    }
    alpha
    {
      col1 = col0.a * tex1.a;
    }
  }
  {
    rgb
    {
      discard = col0.rgb * unsigned_invert(zero.rgb);
      discard = const0.rgb * unsigned_invert(zero.rgb);
      col0 = sum();
    }
    alpha
    {
      col0 = col1.a * tex0.a;
    }
  }
  {
    rgb
    {
      col1 = const0.rgb * col0.a;
      scale_by_two();
    }
    alpha
    {
      col0 = const0.a * col0.a;
      scale_by_two();
    }
  }
  {
    rgb
    {
      discard = tex0.rgb * col0.rgb;
      discard = col1.rgb * unsigned_invert(zero.rgb);
      col0 = sum();
    }
    alpha
    {
      discard = col0.a * unsigned_invert(zero.a);
      discard = const0.a * tex0.a;
      col0 = sum();
    }
  }
  out.rgb = unsigned(col0.rgb);
  out.a = unsigned(col0.a);
  // 10 instructions
  	"
}
SubProgram {
  Type 4
  Local 8, [_PPLAmbient]
  Local 24, [_PPLAmbient]
  Local 16, [_SpecColor]
  SetTexture [_MainTex]
  SetTexture [_SpecCube0]

  "!!TS1.0
  texture_2d();
  texture_cube_map();
  texture_3d();
  !!RC1.0
  {
    rgb
    {
      col0 = tex2.a * col0.rgb;
      scale_by_two();
    }
    alpha
    {
      col0 = tex2.a * tex1.a;
    }
  }
  {
    rgb
    {
      discard = col0.rgb * unsigned_invert(zero.rgb);
      discard = const0.rgb * unsigned_invert(zero.rgb);
      col0 = sum();
    }
    alpha
    {
      col0 = col0.a * tex0.a;
    }
  }
  {
    rgb
    {
      col1 = const0.rgb * col0.a;
      scale_by_two();
    }
    alpha
    {
      col0 = const0.a * col0.a;
      scale_by_two();
    }
  }
  {
    rgb
    {
      discard = tex0.rgb * col0.rgb;
      discard = col1.rgb * unsigned_invert(zero.rgb);
      col0 = sum();
    }
    alpha
    {
      discard = col0.a * unsigned_invert(zero.a);
      discard = const0.a * tex0.a;
      col0 = sum();
    }
  }
  out.rgb = unsigned(col0.rgb);
  out.a = unsigned(col0.a);
  // 8 instructions
  	"
}
SubProgram {
  Type 5
  Local 8, [_PPLAmbient]
  Local 24, [_PPLAmbient]
  Local 16, [_SpecColor]
  SetTexture [_MainTex]
  SetTexture [_SpecCube0]

  "!!TS1.0
  texture_2d();
  texture_cube_map();
  texture_cube_map();
  !!RC1.0
  {
    rgb
    {
      col0 = tex2.a * col0.rgb;
      scale_by_two();
    }
    alpha
    {
      col0 = tex2.a * tex1.a;
    }
  }
  {
    rgb
    {
      discard = col0.rgb * unsigned_invert(zero.rgb);
      discard = const0.rgb * unsigned_invert(zero.rgb);
      col0 = sum();
    }
    alpha
    {
      col0 = col0.a * tex0.a;
    }
  }
  {
    rgb
    {
      col1 = const0.rgb * col0.a;
      scale_by_two();
    }
    alpha
    {
      col0 = const0.a * col0.a;
      scale_by_two();
    }
  }
  {
    rgb
    {
      discard = tex0.rgb * col0.rgb;
      discard = col1.rgb * unsigned_invert(zero.rgb);
      col0 = sum();
    }
    alpha
    {
      discard = col0.a * unsigned_invert(zero.a);
      discard = const0.a * tex0.a;
      col0 = sum();
    }
  }
  out.rgb = unsigned(col0.rgb);
  out.a = unsigned(col0.a);
  // 8 instructions
  	"
}
SubProgram {
  Type 1
  Local 0, [_SpecColor]
  Local 2, [_PPLAmbient]
  SetTexture [_MainTex]
  SetTexture [_SpecCube0]

  "!!ARBfp1.0
  PARAM c[3] = { program.local[0],
  		{ 2 },
  		program.local[2] };
  TEMP R0;
  TEMP R1;
  TEMP R2;
  MUL R2.xyz, fragment.color.primary, c[1].x;
  TEX R0, fragment.texcoord[0], texture[0], 2D;
  TEX R1.w, fragment.texcoord[1], texture[1], CUBE;
  MUL R1.x, R1.w, R0.w;
  MUL R1, R1.x, c[0];
  MUL R1, R1, c[1].x;
  MUL R0.w, R0, c[2];
  ADD R2.xyz, R2, c[2];
  MAD result.color.xyz, R0, R2, R1;
  ADD result.color.w, R1, R0;
  END
  # 10 instructions, 3 R-regs
  	"
}
SubProgram {
  Type 2
  Local 0, [_SpecColor]
  Local 2, [_PPLAmbient]
  SetTexture [_MainTex]
  SetTexture [_SpecCube0]

  "!!ARBfp1.0
  PARAM c[3] = { program.local[0],
  		{ 2 },
  		program.local[2] };
  TEMP R0;
  TEMP R1;
  TEMP R2;
  TXP R0.w, fragment.texcoord[2], texture[2], 2D;
  TEX R2.w, fragment.texcoord[1], texture[1], CUBE;
  MUL R2.xyz, R0.w, fragment.color.primary;
  MUL R2.xyz, R2, c[1].x;
  TEX R1, fragment.texcoord[0], texture[0], 2D;
  MUL R0.x, R0.w, R2.w;
  MUL R0.x, R0, R1.w;
  MUL R0, R0.x, c[0];
  MUL R0, R0, c[1].x;
  MUL R2.w, R1, c[2];
  ADD R2.xyz, R2, c[2];
  MAD result.color.xyz, R1, R2, R0;
  ADD result.color.w, R0, R2;
  END
  # 13 instructions, 3 R-regs
  	"
}
SubProgram {
  Type 3
  Local 0, [_SpecColor]
  Local 2, [_PPLAmbient]
  SetTexture [_MainTex]
  SetTexture [_SpecCube0]

  "!!ARBfp1.0
  PARAM c[3] = { program.local[0],
  		{ 2 },
  		program.local[2] };
  TEMP R0;
  TEMP R1;
  TEMP R2;
  TEMP R3;
  TEX R3, fragment.texcoord[0], texture[0], 2D;
  TEX R0.w, fragment.texcoord[1], texture[1], CUBE;
  TXP R1.w, fragment.texcoord[2], texture[2], 2D;
  TXP R2.w, fragment.texcoord[3], texture[3], 2D;
  MUL R0.y, R1.w, R2.w;
  MUL R0.x, R0.y, R0.w;
  MUL R1.xyz, R0.y, fragment.color.primary;
  MUL R0.x, R0, R3.w;
  MUL R0, R0.x, c[0];
  MUL R1.xyz, R1, c[1].x;
  MUL R0, R0, c[1].x;
  MUL R1.w, R3, c[2];
  ADD R1.xyz, R1, c[2];
  MAD result.color.xyz, R3, R1, R0;
  ADD result.color.w, R0, R1;
  END
  # 15 instructions, 4 R-regs
  	"
}
SubProgram {
  Type 4
  Local 0, [_SpecColor]
  Local 2, [_PPLAmbient]
  SetTexture [_MainTex]
  SetTexture [_SpecCube0]

  "!!ARBfp1.0
  PARAM c[3] = { program.local[0],
  		{ 2 },
  		program.local[2] };
  TEMP R0;
  TEMP R1;
  TEMP R2;
  TEX R0.w, fragment.texcoord[2], texture[2], 3D;
  TEX R2.w, fragment.texcoord[1], texture[1], CUBE;
  MUL R2.xyz, R0.w, fragment.color.primary;
  MUL R2.xyz, R2, c[1].x;
  TEX R1, fragment.texcoord[0], texture[0], 2D;
  MUL R0.x, R0.w, R2.w;
  MUL R0.x, R0, R1.w;
  MUL R0, R0.x, c[0];
  MUL R0, R0, c[1].x;
  MUL R2.w, R1, c[2];
  ADD R2.xyz, R2, c[2];
  MAD result.color.xyz, R1, R2, R0;
  ADD result.color.w, R0, R2;
  END
  # 13 instructions, 3 R-regs
  	"
}
SubProgram {
  Type 5
  Local 0, [_SpecColor]
  Local 2, [_PPLAmbient]
  SetTexture [_MainTex]
  SetTexture [_SpecCube0]

  "!!ARBfp1.0
  PARAM c[3] = { program.local[0],
  		{ 2 },
  		program.local[2] };
  TEMP R0;
  TEMP R1;
  TEMP R2;
  TEX R0.w, fragment.texcoord[2], texture[2], CUBE;
  TEX R2.w, fragment.texcoord[1], texture[1], CUBE;
  MUL R2.xyz, R0.w, fragment.color.primary;
  MUL R2.xyz, R2, c[1].x;
  TEX R1, fragment.texcoord[0], texture[0], 2D;
  MUL R0.x, R0.w, R2.w;
  MUL R0.x, R0, R1.w;
  MUL R0, R0.x, c[0];
  MUL R0, R0, c[1].x;
  MUL R2.w, R1, c[2];
  ADD R2.xyz, R2, c[2];
  MAD result.color.xyz, R1, R2, R0;
  ADD result.color.w, R0, R2;
  END
  # 13 instructions, 3 R-regs
  	"
}

}
				SetTexture [_MainTex]{ combine previous}
				SetTexture [_SpecCube0] { combine previous }
				SetTexture [_LightTexture0] { combine previous} 
				SetTexture [_LightTextureB0]{ combine previous}
			}
		}

		// ---------------------------------------------
		// R9000 
		// ---------------------------------------------
		SubShader {
			Lighting On
			Pass {
				Tags {"LightMode" = "None"}
				Color [_ModelAmbient]

				SetTexture [_MainTex] {Combine texture * primary
			}
			}
			Pass { 
				 Tags {"LightMode" = "Vertex"}
				Lighting On
				Material {
					Diffuse [_Color]
					Ambient (1,1,1,1)
				}
			 	SetTexture [_MainTex] {Combine texture * primary DOUBLE, texture * primary}
			}
			Pass { 
				Tags {"LightMode" = "Vertex"}
				Blend One One
				Material {
					Specular [_SpecColor]
					Shininess [_Shininess]
				}
				colormask RGB		// Very important: gloss is now in alpha, so leave it
				Lighting On
				Fog { Color (0,0,0,0) } 
				SetTexture [_MainTex] {Combine texture alpha* primary}
			} 
			Pass { 
				Tags { 
					"LightMode" = "Pixel" 
					"LightTexCount" = "0"
				}
				Blend AppSrcAdd AppDstAdd
				Fog { Color [_AddFog] }
				Lighting On
				Material {
					Diffuse [_Color]
				}
				ColorMask RGB
				Program "" {
					SubProgram {
					Local 0, [_SpecColor]
					Local 1, [_Color]

"!!ATIfs1.0
StartConstants;
	CONSTANT c0 = program.local[0];
	CONSTANT c1 = program.local[1];
EndConstants;
StartOutputPass;
	SampleMap r0, t0.stq_dq;	# main texture
	SampleMap r1, t1.str;	# specmap

	# r2 = light0 contribution
	MUL r0.rgb.2x, r0, color0; 

	MUL r1.rgb.2x, r0.a, r1;
	MAD r0.rgb, r1, c0, r0;
	MUL r0.a, r0.a, c1.a;
EndPass;
"
					}
				}
				SetTexture [_MainTex] {combine previous}
				SetTexture [_SpecCube0] {combine primary}
			}
			Pass { 
				Tags { 
					"LightMode" = "Pixel" 
					"LightTexCount" = "1"
				}
				Blend AppSrcAdd AppDstAdd
				Fog { Color [_AddFog] }
				Lighting On
				ColorMask RGB

				Material {
					Diffuse [_Color]
				}
				Program "" {
					SubProgram {
						Local 0, [_SpecColor]
						Local 1, [_PPLAmbient]
						Local 2, [_Color]
						Type 2
"!!ATIfs1.0
StartConstants;
	CONSTANT c0 = program.local[0];
	CONSTANT c1 = program.local[1];
	CONSTANT c2 = program.local[2];
EndConstants;
StartOutputPass;
	SampleMap r0, t0.stq_dq;	# main texture
	SampleMap r1, t1.str;	# specmap
	SampleMap r2, t2.stq_dq;	# light cookie

	MAD r3, color0, r2.a, c1;	# diffuse light color
	MUL r0.rgb.2x, r0, r3; 	# final = 2 * tex * diff
	MUL r1.a, r0, r1;
	MUL r1.a, r1, r2;
	MUL r1.rgb.2x, r0.a, r1;
 	MAD r0.rgb, r1.a, c0, r0;
	MUL r0.a, r0.a, c2.a;
EndPass;
"
					}
					SubProgram {
						Local 0, [_SpecColor]
						Local 1, [_PPLAmbient]
						Local 2, [_Color]
"!!ATIfs1.0
StartConstants;
	CONSTANT c0 = program.local[0];
	CONSTANT c1 = program.local[1];
	CONSTANT c2 = program.local[2];
EndConstants;
StartOutputPass;
	SampleMap r0, t0.stq_dq;	# main texture
	SampleMap r1, t1.str;	# specmap
	SampleMap r2, t2.str;	# light cookie

	MAD r3, color0, r2.a, c1;	# diffuse light color
	MUL r0.rgb.2x, r0, r3; 	# final = 2 * tex * diff
	MUL r1.a, r0, r1;
	MUL r1.a, r1, r2;
	MUL r1.rgb.2x, r0.a, r1;
 	MAD r0.rgb, r1.a, c0, r0;
	MUL r0.a, r0.a, c2.a;
EndPass;
"
					}
				}
				SetTexture [_MainTex] {combine primary}
				SetTexture [_SpecCube0] {combine primary}
				SetTexture [_LightTexture0] {combine primary}
			}
			Pass { 
				Tags { 
					"LightMode" = "Pixel" 
					"LightTexCount" = "2"
				}
				Blend AppSrcAdd AppDstAdd
				Fog { Color [_AddFog] }
				Lighting On
				Material {
					Diffuse [_Color]
				}
				Program "" {
					SubProgram {
						Local 0, [_SpecColor]
						Local 1, [_PPLAmbient]
"!!ATIfs1.0
StartConstants;
	CONSTANT c0 = program.local[0];
	CONSTANT c1 = program.local[1];
EndConstants;
StartOutputPass;
	SampleMap r0, t0.stq_dq;	# main texture
	SampleMap r1, t1.str;	# specmap
	SampleMap r2, t2.stq_dq;	# light cookie
	SampleMap r3, t3.stq_dq;	# light cookie

	MUL r2.a, r2.a, r3.a;

	MAD r3, color0, r2.a, c1;	# diffuse light color
	MUL r0.rgb.2x, r0, r3; 	# final = 2 * tex * diff
	MUL r1.a, r0, r1;
	MUL r1.a, r1, r2;
	MUL r1.rgb.2x, r0.a, r1;
 	MAD r0.rgb, r1.a, c0, r0;
EndPass;
"
					}
				}
				SetTexture [_MainTex]
				SetTexture [_SpecCube0] {combine primary}
				SetTexture [_LightTexture0] {combine primary}
				SetTexture [_LightTextureB0] {combine primary}
			}
		}

		// ---------------------------------------------------------
		// R7000 shader
		// ---------------------------------------------------------
		SubShader {
			Lighting On
			Pass { 
				Tags {"LightMode" = "PixelOrNone"}
				Color [_PPLAmbient]
				SetTexture [_MainTex] {Combine texture * primary DOUBLE, texture}
				SetTexture [_MainTex] {Combine texture * primary DOUBLE, texture}
				SetTexture [_MainTex] {constantColor [_Color] Combine  texture * primary DOUBLE, texture * constant}
			}
			Pass { 
				Tags {"LightMode" = "vertex"}
				Material {
					Diffuse [_Color]
					Emission [_PPLAmbient]
				}
				Lighting On
				SetTexture [_MainTex] {Combine texture * primary DOUBLE, texture}
				SetTexture [_MainTex] {Combine texture * primary DOUBLE, texture}
				SetTexture [_MainTex] {constantColor [_Color] Combine  texture * primary DOUBLE, texture * constant}
			} 
			Pass { 
				Tags {"LightMode" = "Vertex"}
				Blend Zero One
				Material {
					Specular [_SpecColor]
					Shininess [_Shininess]
				}
				colormask RGB		// Very important: gloss is now in alpha, so leave it
				Lighting On
				Fog { Color (0,0,0,0) } 
				SetTexture [_MainTex] {Combine texture alpha* primary DOUBLE}
			} 
			Pass {
				Tags {
					"LightMode" = "Pixel" 
				}
				Fog { Color [_AddFog] }
				Blend AppSrcAdd AppDstAdd
				colormask RGB		// Very important: gloss is now in alpha, so leave it
				Material {
					Diffuse [_Color]
				}
				Lighting On
				SetTexture [_LightTexture0]	{ combine previous * texture alpha }
				SetTexture [_LightTextureB0]	{ 
					combine previous * texture alpha + constant, previous
					constantColor [_PPLAmbient]
				}
				SetTexture [_MainTex] 		{ combine previous * texture DOUBLE}
			}
			Pass {
				Tags {
					"LightMode" = "Pixel" 
				}
				Blend DstAlpha One
				colormask RGB		// Very important: gloss is now in alpha, so leave it
				Color [_SpecColor]
				Offset -1, -1
				Fog { color (0,0,0,0) }
				AlphaTest Greater 0
				ZWrite off
				SetTexture [_LightTexture0] { combine primary * texture alpha, texture alpha}
				SetTexture [_LightTextureB0] {combine previous * texture alpha, previous * texture alpha}
				SetTexture [_SpecCube0] { 
					combine previous * texture alpha, previous * texture alpha
				}
			}
		}
	}
	Fallback " Diffuse", 1
}
