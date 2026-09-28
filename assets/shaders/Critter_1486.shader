Shader "GooBall/Critter" {
	Properties {
		_Color ("Main Color", Color) = (1,1,1,1)
		_Shininess ("Shininess", range (0,1)) = 0.1
		_Highlight ("Highlight size", range (0,64)) = 30
		_MainTex ("Base (RGB)", 2D) = "ah64rotor1"
	}

	Category {
		SubShader {
			Material {
				Diffuse [_Color]
				Specular ([_Shininess], [_Shininess], [_Shininess], 0)
				Shininess [_Highlight]
				Ambient  [_Color]
				Emission [_PPLAmbient]
			}
			Tags { "Queue" = "Critter" }
			Pass {
//				ColorMask RGB
				Lighting On
				SetTexture [_MainTex] {Combine texture * primary DOUBLE, constant constantColor (1,0,0,0)}
			}
		}
	}
}
