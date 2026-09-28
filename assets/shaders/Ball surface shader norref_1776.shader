// GooBall ball shader

// Written by Nicholas Francis. Copyright OTE 2003

SHADER "GooBall/norref ball" { 
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
		_SANoCube ("alpha spheremap", 2D) = "wood0.jpg" { 
			TexGen SphereMap
		}
		_SACube ("self-illumin/alpha cubemap", Cube) = "wood0.jpg" { 
			TexGen CubeReflect
		}
		_SpecCube ("Specular cubemap", Cube) = "wood0.jpg" { 
			TexGen CubeReflect
		}
		_SpecCube2 ("inv. Specular cubemap", Cube) = "wood0.jpg" { 
			TexGen CubeReflect
		}
		_SpecCube3 ("PPL Specular cubemap", Cube) = "wood0.jpg" { 
		}
	}
	// r7000, Geforce3, R8000
	SubShader {
		Tags { "Queue" ="Transparent" }
		// Inside of ball
		Pass {
			Cull Front
			Offset -2, -2
			Blend OneMinusSrcAlpha SrcAlpha
			// Load the OpenGL material info from the properties above
			SetTexture [_SACube] {
				constantcolor ([_SelfIllumin], [_SelfIllumin], [_SelfIllumin], [_BackAlpha])
				combine texture * constant
			}
			SetTexture [_MainTex] {
				combine texture * previous DOUBLE, previous * texture 
			}
		}
		// Front of ball
		Pass {

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
			Cull Front
			Offset -2, -2
			Blend OneMinusSrcAlpha SrcAlpha
			// Load the OpenGL material info from the properties above
			SetTexture [_SACube] {
				constantcolor ([_SelfIllumin], [_SelfIllumin], [_SelfIllumin], [_BackAlpha])
				combine texture * constant
			}
			SetTexture [_MainTex] {
				combine texture * previous DOUBLE, previous * texture 
			}
		}

		// Front of ball
		Pass {

			ColorMask RGB
			Material {
				Emission [_Emissions]
				Diffuse [_Color]
				Ambient (1,1,1,1)
			}
			Lighting On
			// Load the OpenGL material info from the properties above
			Blend SrcAlpha OneMinusSrcAlpha
	/*		SetTexture [_SACube] {
				constantcolor (0,0,0, [_FrontAlpha])
				combine texture * primary DOUBLE, texture * constant
			}*/
			SetTexture [_MainTex] {
				combine texture * previous, previous 
			}
		}
		// Front of ball
		Pass {

			Material {
				Emission [_Emissions]
				Diffuse [_Color]
				Ambient (1,1,1,1)
			}
			Lighting On
			// Load the OpenGL material info from the properties above
			Blend One One
			SetTexture [_SpecCube] {		// Apply the texture from the properties
				constantColor [_SpecCol]
				combine texture *constant alpha
			}
		}
	}
	// ATI rage
	SubShader {
		Tags { "Queue" = "Transparent" }
		Pass {
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
