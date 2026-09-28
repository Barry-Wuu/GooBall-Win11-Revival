// GooBall ball shader

// Written by Nicholas Francis. Copyright OTE 2003

SHADER "GooBall/GDC demo ball" { 
    Properties {
		_SpecCol ("Specular Color", Color) = (.2,.2,.2,1)
		_Color ("Main Color", Color) = (.5, .5,.5,1)
		_Emissions ("Emission", Color) = (1,1,1,1)
		_SelfIllumin ("Self-Illumin", range (0,1)) = 1
		_FrontAlpha ("Front Alpha", range (0,1)) = 1
		_BackAlpha ("Back Alpha", range (0,1)) = 1
		_MainTex ("Main Texture", 2d) = "wood0.jpg" {}
		_SpecTex ("spec Texture", 2d) = "wood0.jpg" { 
			TexGen SphereMap
		}
		_SACube ("self-illumin/alpha cubemap", Cube) = "wood0.jpg" { 
			TexGen CubeReflect
		}
		_SANoCube ("alpha spheremap", 2D) = "wood0.jpg" { 
			TexGen SphereMap
		}
		_SpecCube ("Specular cubemap", Cube) = "wood0.jpg" { 
			TexGen CubeReflect
		}
		_SpecCube2 ("inv. Specular cubemap", Cube) = "wood0.jpg" { 
			TexGen CubeReflect
		}
		_SpecCube3 ("PPL Specular cubemap", Cube) = "wood0.jpg" { 
		}
		_GrabTexture ("Grab Texture", Rect) = "" { 
			TexGen SphereMap
		}
	}
// DEBUG REFLECTIONS
/*	SubShader {
		Tags { "Queue" ="Transparent" }
		// Inside of ball
		Pass {
			Tags {
//				"LightMode" = "Vertex"
//				"LightCount" = "0"
			}
			Cull Front
			Offset -2, -2
			Lighting On
			// Load the OpenGL material info from the properties above
			SetTexture [_GrabTexture] { 
				constantColor (0,0,0,0)
				combine texture, CONSTANT
			}
		}
	}*/

	
	// REFRACTION VERSION... r7000, Geforce3, R8000
	SubShader {
		Tags { "Queue" ="Transparent" }
		// Inside of ball
		Pass {
			Lighting On
			Cull Front
			Offset -2, -2
			// Load the OpenGL material info from the properties above
			SetTexture [_SACube] {
				constantcolor ([_SelfIllumin], [_SelfIllumin], [_SelfIllumin], [_BackAlpha])
				combine texture * constant, constant
			}
			SetTexture [_GrabTexture] { 
				constantColor (0,0,0,0)
				combine texture, CONSTANT
			}
			// Get the glow for the specular highlights.
			SetTexture [_SpecCube2] {		
				constantColor [_SpecCol]
				combine previous, previous + texture  // Modulate in with the primary color
			}
		}

		// Front of ball
		Pass {
			Lighting On
			ColorMask RGB
			Material {
				Emission [_Emissions]
				Diffuse [_Color]
				Ambient (1,1,1,1)
			}
			Lighting On
			// Load the OpenGL material info from the properties above
			Blend SrcAlpha OneMinusSrcAlpha
/*			SetTexture [_SACube] {
				constantcolor (0,0,0, [_FrontAlpha])
				combine texture * primary DOUBLE, texture * constant
			}*/
			SetTexture [_MainTex] {
				combine texture * previous, previous 
			}
			SetTexture [_SpecCube] {		// Apply the texture from the properties
				constantColor [_SpecCol]
				combine texture *constant + previous, previous + texture  // Modulate in with the primary color
			}
		}

	}

	// Geforce MX
	SubShader {
		Tags { "Queue" ="Transparent" }
		// Inside of ball
		Pass {
			Tags {
				"LightMode" = "VertexOrPixel"
				"LightCount" = "0"
			}
			Lighting On
			Cull Front
			Offset -2, -2
			// Load the OpenGL material info from the properties above
			SetTexture [_SACube] {
				constantcolor ([_SelfIllumin], [_SelfIllumin], [_SelfIllumin], [_BackAlpha])
				combine texture * constant, constant
			}
			SetTexture [_GrabTexture] { 
				constantColor (0,0,0,0)
				combine texture, CONSTANT
			}
		}
		// Front of ball
		Pass {
			Lighting On
			ColorMask RGB
			Material {
				Emission [_Emissions]
				Diffuse [_Color]
				Ambient (1,1,1,1)
			}
			Lighting On
			// Load the OpenGL material info from the properties above
			Blend SrcAlpha OneMinusSrcAlpha
/*			SetTexture [_SACube] {
				constantcolor (0,0,0, [_FrontAlpha])
				combine texture * primary DOUBLE, texture * constant
			}*/
			SetTexture [_MainTex] {
				combine texture * previous, previous 
			}
		}
		// Specular highlights

		Pass {
			Lighting On
			Fog { Color (0,0,0,0) }
			// Load the OpenGL material info from the properties above
			Blend One One
			SetTexture [_SpecCube] {		// Apply the texture from the properties
				constantColor [_SpecCol]
				combine texture *constant alpha, texture  // Modulate in with the primary color
			}
		}
	}
	// ATI rage
	SubShader {
		Tags { "Queue" = "Transparent" }
		Pass {
			Lighting On
			Material {
				Emission [_Emissions]
				Diffuse [_Color]
				Ambient (1,1,1,1)
			}
			Lighting On
			ZWrite Off
			// Load the OpenGL material info from the properties above
			Blend SrcAlpha OneMinusSrcAlpha
			SetTexture [_MainTex] {
				constantColor (0,0,0,1)
				combine texture * previous, texture * constant
			}
			SetTexture [_SpecTex] {
				combine texture + previous, texture * previous
			}
		}
	}

}
