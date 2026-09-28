Shader "GooBall/Toony" {
	Properties {
		_Color ("Main Color", Color) = (1,1,1,1)
		_EdgeColor ("Main Color", Color) = (1,1,1,1)
		_MainTex ("Base (RGB) Ref. strength (A)", 2D) = ""
		_BackTex ("Reflection cube (RGB)", CUBE) = "" {
			TexGen CubeReflect 
		}
	}
	Category {
		tags { "lod" = "0" }
		// R7000 shader
		SubShader {
			Material {
				Diffuse [_Color]
				Ambient [_Color]
			}
			Lighting On
			Fog { Color [_AddFog] }
			Blend AppSrcAdd AppDstAdd
			Pass { 
				Tags {"LightMode" = "PixelOrNone"}
				Color [_PPLAmbient]
				SetTexture [_MainTex] { Combine texture * primary DOUBLE, texture}
				SetTexture [_BackTex] { 
					constantColor [_EdgeColor]
					Combine constant * texture + previous, primary * previous
				}
			}
			Pass { 
				Tags {"LightMode" = "vertex"}
				Material {
					Diffuse [_Color]
					Ambient [_Color]
				}
				Lighting On
				SetTexture [_MainTex] { Combine texture * primary DOUBLE, texture }
				SetTexture [_BackTex] { 
					constantColor [_EdgeColor]
					Combine constant * texture + previous, primary * previous
				}
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
				SetTexture [_MainTex] 	{ combine previous * texture DOUBLE, constant}
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
				SetTexture [_MainTex] 	{ combine previous * texture DOUBLE, constant}
			}
			Pass {
				Tags {
					"LightMode" = "Pixel" 
					"LightTexCount"  = "0"
				}
				ColorMask RGB
				SetTexture [_MainTex] 	{ combine previous * texture DOUBLE, constant}
			}
		}
	}
	Fallback " Diffuse", 1
}

