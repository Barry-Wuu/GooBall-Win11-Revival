Shader " Diffuse" {
	Properties {
		_Color ("Main Color", Color) = (1,1,1,1)
		_MainTex ("Base (RGB) Gloss (A)", 2D) = "ah64rotor1"
	}
	Category {
		Lod 0
	 	// ------------------------------------------------------
	 	// ARB_FP, Geforce3
	 	// ------------------------------------------------------
/*		SubShader {
			TexCount 4		// Get Geforce2s to ignore this shader
			Pass {					// Ambient only
				Tags {"LightMode" = "None"}
				Fog {  Color [_AddFog] }
				Blend AppSrcAdd AppDstAdd
				Color [_PPLAmbient]
				SetTexture [_MainTex] {constantColor [_Color] Combine texture * primary DOUBLE, texture *  constant}
			}
			Pass { 
				Tags {"LightMode" = "Vertex"} 
				Fog {  Color [_AddFog] }
 				Blend AppSrcAdd AppDstAdd
				Material {
					Diffuse [_Color]
					Emission [_PPLAmbient]
				}
				Lighting On
				SetTexture [_MainTex] {constantColor [_PPLAmbent] Combine texture * primary DOUBLE, texture *  primary}
			}
			Pass {	
				// Sum all light contribs from 2-tex lights
				Tags { 
					"LightMode" = "Pixel" 
				}
				Blend AppSrcAdd AppDstAdd
				Fog { Color [_AddFog] }
				Material { Diffuse [_Color] }
				Lighting On

Program "" {
SubProgram {
  Type 1
  Local 0, [_PPLAmbient]
  SetTexture [_MainTex]

  "!!TS1.0
  texture_2d();
  !!RC1.0
  {
    rgb
    {
      discard = col0.rgb * unsigned_invert(zero.rgb);
      discard = const0.rgb * unsigned_invert(zero.rgb);
      col0 = sum();
    }
    alpha
    {
      col0 = tex0.a * const0.a;
    }
  }
  {
    rgb
    {
      col0 = tex0.rgb * col0.rgb;
      scale_by_two();
    }
  }
  out.rgb = unsigned(col0.rgb);
  out.a = unsigned(col0.a);
  	"
}
SubProgram {
  Type 2
  Local 0, [_PPLAmbient]
  SetTexture [_MainTex]

  "!!TS1.0
  texture_2d();
  texture_2d();
  !!RC1.0
  {
    rgb
    {
      discard = tex1.a * col0.rgb;
      discard = const0.rgb * unsigned_invert(zero.rgb);
      col0 = sum();
    }
    alpha
    {
      col0 = tex0.a * const0.a;
    }
  }
  {
    rgb
    {
      col0 = tex0.rgb * col0.rgb;
      scale_by_two();
    }
  }
  out.rgb = unsigned(col0.rgb);
  out.a = unsigned(col0.a);
  	"
}
SubProgram {
  Type 3
  Local 0, [_PPLAmbient]
  Local 8, [_PPLAmbient]
  SetTexture [_MainTex]

  "!!TS1.0
  texture_2d();
  texture_2d();
  texture_2d();
  !!RC1.0
  {
    alpha
    {
      col0 = tex1.a * tex2.a;
      col1 = tex0.a * const0.a;
    }
  }
  {
    rgb
    {
      discard = col0.a * col0.rgb;
      discard = const0.rgb * unsigned_invert(zero.rgb);
      col0 = sum();
    }
  }
  {
    rgb
    {
      col0 = tex0.rgb * col0.rgb;
      scale_by_two();
    }
  }
  out.rgb = unsigned(col0.rgb);
  out.a = unsigned(col1.a);
  	"
}
SubProgram {
  Type 4
  Local 0, [_PPLAmbient]
  SetTexture [_MainTex]

  "!!TS1.0
  texture_2d();
  texture_3d();
  !!RC1.0
  {
    rgb
    {
      discard = tex1.a * col0.rgb;
      discard = const0.rgb * unsigned_invert(zero.rgb);
      col0 = sum();
    }
    alpha
    {
      col0 = tex0.a * const0.a;
    }
  }
  {
    rgb
    {
      col0 = tex0.rgb * col0.rgb;
      scale_by_two();
    }
  }
  out.rgb = unsigned(col0.rgb);
  out.a = unsigned(col0.a);
  	"
}
SubProgram {
  Type 5
  Local 0, [_PPLAmbient]
  SetTexture [_MainTex]

  "!!TS1.0
  texture_2d();
  texture_cube_map();
  !!RC1.0
  {
    rgb
    {
      discard = tex1.a * col0.rgb;
      discard = const0.rgb * unsigned_invert(zero.rgb);
      col0 = sum();
    }
    alpha
    {
      col0 = tex0.a * const0.a;
    }
  }
  {
    rgb
    {
      col0 = tex0.rgb * col0.rgb;
      scale_by_two();
    }
  }
  out.rgb = unsigned(col0.rgb);
  out.a = unsigned(col0.a);
  	"
}
SubProgram {
  Type 1
  Local 0, [_PPLAmbient]
  SetTexture [_MainTex]

  "!!ARBfp1.0
OPTION ARB_fog_exp2;
OPTION ARB_precision_hint_fastest;
  PARAM u0 = program.local[0];
  PARAM c0 = {2, 0, 0, 0};
  TEMP R0;
  TEMP R1;
  TEMP H0;
  TEMP H1;
  TEX R0, fragment.texcoord[0], texture[0], 2D;
  MOV H0.w, R0.w;
  ADD R1.xyz, fragment.color.primary, u0;
  MUL R1.xyz, R0, R1;
  MOV H0.xyz, R1;
  MOV H1.w, H0.w;
  MUL H0.xyz, H0, c0.x;
  MOV H1.xyz, H0;
  MOV H0.xyz, H1;
  MUL R0.x, H1.w, u0.w;
  MOV H0.w, R0.x;
  MOV result.color, H0;
  END
  	"
}
SubProgram {
  Type 2
  Local 0, [_PPLAmbient]
  SetTexture [_MainTex]

  "!!ARBfp1.0
OPTION ARB_fog_exp2;
OPTION ARB_precision_hint_fastest;
  PARAM u0 = program.local[0];
  PARAM c0 = {2, 0, 0, 0};
  TEMP R0;
  TEMP R1;
  TEMP H0;
  TEMP H1;
  TXP R0.w, fragment.texcoord[1], texture[1], 2D;
  TEX R1, fragment.texcoord[0], texture[0], 2D;
  MAD R0.xyz, R0.w, fragment.color.primary, u0;
  MUL R0.xyz, R1, R0;
  MOV H0.w, R1.w;
  MOV H0.xyz, R0;
  MOV H1.w, H0.w;
  MUL H0.xyz, H0, c0.x;
  MOV H1.xyz, H0;
  MOV H0.xyz, H1;
  MUL R0.x, H1.w, u0.w;
  MOV H0.w, R0.x;
  MOV result.color, H0;
  END
  	"
}
SubProgram {
  Type 3
  Local 0, [_PPLAmbient]
  SetTexture [_MainTex]

  "!!ARBfp1.0
OPTION ARB_fog_exp2;
OPTION ARB_precision_hint_fastest;
  PARAM u0 = program.local[0];
  PARAM c0 = {2, 0, 0, 0};
  TEMP R0;
  TEMP R1;
  TEMP H0;
  TEMP H1;
  TXP R0.w, fragment.texcoord[1], texture[1], 2D;
  TXP R1.w, fragment.texcoord[2], texture[2], 2D;
  MUL R0.x, R0.w, R1.w;
  MAD R0.xyz, R0.x, fragment.color.primary, u0;
  TEX R1, fragment.texcoord[0], texture[0], 2D;
  MUL R0.xyz, R1, R0;
  MOV H0.w, R1.w;
  MOV H0.xyz, R0;
  MOV H1.w, H0.w;
  MUL H0.xyz, H0, c0.x;
  MOV H1.xyz, H0;
  MOV H0.xyz, H1;
  MUL R0.x, H1.w, u0.w;
  MOV H0.w, R0.x;
  MOV result.color, H0;
  END
  	"
}
SubProgram {
  Type 4
  Local 0, [_PPLAmbient]
  SetTexture [_MainTex]

  "!!ARBfp1.0
OPTION ARB_fog_exp2;
OPTION ARB_precision_hint_fastest;
  PARAM u0 = program.local[0];
  PARAM c0 = {2, 0, 0, 0};
  TEMP R0;
  TEMP R1;
  TEMP H0;
  TEMP H1;
  TEX R0.w, fragment.texcoord[1], texture[1], 3D;
  TEX R1, fragment.texcoord[0], texture[0], 2D;
  MAD R0.xyz, R0.w, fragment.color.primary, u0;
  MUL R0.xyz, R1, R0;
  MOV H0.w, R1.w;
  MOV H0.xyz, R0;
  MOV H1.w, H0.w;
  MUL H0.xyz, H0, c0.x;
  MOV H1.xyz, H0;
  MOV H0.xyz, H1;
  MUL R0.x, H1.w, u0.w;
  MOV H0.w, R0.x;
  MOV result.color, H0;
  END
  	"
}
SubProgram {
  Type 5
  Local 0, [_PPLAmbient]
  SetTexture [_MainTex]

  "!!ARBfp1.0
OPTION ARB_fog_exp2;
OPTION ARB_precision_hint_fastest;
  PARAM u0 = program.local[0];
  PARAM c0 = {2, 0, 0, 0};
  TEMP R0;
  TEMP R1;
  TEMP H0;
  TEMP H1;
  TEX R0.w, fragment.texcoord[1], texture[1], CUBE;
  TEX R1, fragment.texcoord[0], texture[0], 2D;
  MAD R0.xyz, R0.w, fragment.color.primary, u0;
  MUL R0.xyz, R1, R0;
  MOV H0.w, R1.w;
  MOV H0.xyz, R0;
  MOV H1.w, H0.w;
  MUL H0.xyz, H0, c0.x;
  MOV H1.xyz, H0;
  MOV H0.xyz, H1;
  MUL R0.x, H1.w, u0.w;
  MOV H0.w, R0.x;
  MOV result.color, H0;
  END
  	"
}

}

 

				SetTexture [_MainTex]{ combine texture * primary DOUBLE}
				SetTexture [_LightTexture0] { combine previous * texture alpha} 
				SetTexture [_LightTextureB0]{ combine previous}
			}
		}
*/		// ------------------------------------------------------
		// Radeon7000 +9000 series subshader
		// ------------------------------------------------------
		Category {
			Material {
				Diffuse [_Color]
				Emission [_PPLAmbient]
			}
			Lighting On
			Fog { Color [_AddFog] }
			Blend AppSrcAdd AppDstAdd
			SubShader {
				Pass {
					Tags {"LightMode" = "None"}
					Color [_PPLAmbient]
					Lighting Off
					SetTexture [_MainTex] {Combine texture * primary DOUBLE}
					SetTexture [_MainTex] {Combine texture * primary DOUBLE}
					SetTexture [_MainTex] {Combine texture * primary DOUBLE, primary * texture}
				}
				Pass { 
					Tags {"LightMode" = "Vertex"}
					SetTexture [_MainTex] {Combine texture * primary DOUBLE, primary * texture}
				}
				Pass {
					Tags {
						"LightMode" = "Pixel" 
						"LightTexCount"  = "2"
					}
					ColorMask RGB
					SetTexture [_LightTexture0] 	{ combine previous * texture alpha, previous }
					SetTexture [_LightTextureB0]	{ 
						combine previous * texture alpha + constant, previous
						constantColor [_PPLAmbient]
					}
					SetTexture [_MainTex] 	{ combine previous * texture DOUBLE}
				}
				Pass {
					Tags {
						"LightMode" = "Pixel" 
						"LightTexCount"  = "1"
					}
					ColorMask RGB
					SetTexture [_LightTexture0] { 
						combine previous * texture alpha + constant, previous
						constantColor [_PPLAmbient]
					 }
					SetTexture [_MainTex] 	{ combine previous * texture DOUBLE}
				}
				Pass {
					Tags {
						"LightMode" = "Pixel" 
						"LightTexCount"  = "0"
					}
					ColorMask RGB
					SetTexture [_MainTex] 	{ combine previous * texture DOUBLE}
				}
			}
		}

	 	// ------------------------------------------------------
	 	// GeforceMX
	 	// ------------------------------------------------------
 	SubShader {
		Pass {					// Ambient only
			Tags {"LightMode" = "None"}
			Blend AppSrcAdd AppDstAdd
			Color [_PPLAmbient]
			SetTexture [_MainTex] {
				Combine texture * primary DOUBLE, texture * primary
			}
		}

		Pass {	// Sum all light contribs from 2-tex lights
			Tags {
				"LightMode" = "Pixel" 
				"LightTexCount" = "2"
			}
			Blend AppSrcAdd AppDstAdd
			Material {
				Diffuse [_Color]
			}
			Lighting On
Program "" {
SubProgram {
  Local 0, [_PPLAmbient]
  Local 1 , [_Color]

  "!!RC1.0
  {   
    alpha {
	spare1 = tex0.a * tex1.a; 
    } 
  }
  {
    rgb {
	discard = spare1.a * col0.rgb;
	discard = const0.rgb;
	col0 = sum(); 
   }
    alpha { 
	col0 = const0;
    } 
  }
  out.rgb = unsigned(col0.rgb);
  out.a = unsigned(col0.a);
  " 
}

}
			SetTexture [_LightTexture0] { combine texture alpha}
			SetTexture [_LightTextureB0]{ combine texture alpha * previous}
		}
		Pass {
			Tags {
				"LightMode" = "Pixel" 		// Per-pixel mode
				"LightTexCount" = "2"		// 2-tex only
				"LightCount" = "0"			// Only refnder this pass once
			}
			Blend DstColor SrcColor
			SetTexture [_MainTex] { constantColor (0,0,0,.5) combine texture, constant }
		}
		Pass {	// add in 1-tex lights
			Tags {
				"LightMode" = "Pixel" 
				"LightTexCount" = "01"
			}
			Blend AppSrcAdd AppDstAdd
			Lighting On
			Material {
				Diffuse [_Color]
			}
Program "" {
SubProgram {
  Local 0, [_PPLAmbient]
  "!!RC1.0
  {
    rgb {
      discard = col0.rgb * tex0.a;
      discard = const0.rgb;
      col0 = sum();
    }
    alpha {
	col0 = const0 * tex0.a;
    }
  }
  {
    rgb
    {
      col0 = col0.rgb * tex1.rgb;
      scale_by_two();
    }
  }
  out.rgb = unsigned(col0.rgb);
  out.a = unsigned(col0.a);
  "
}
}
			SetTexture [_LightTexture0] { combine texture alpha}
			SetTexture [_MainTex] {combine texture}
		}
		Pass { 
			Tags {"LightMode" = "Vertex"}
			Blend AppSrcAdd AppDstAdd
			Material {
				Diffuse [_Color]
				Emission [_PPLAmbient]
			}
			Lighting On
			SetTexture [_MainTex] { constantColor [_PPLAmbient] Combine texture * primary DOUBLE, texture *  constant}
		}
	}	

	}
	Fallback " VertexLit", 2
}