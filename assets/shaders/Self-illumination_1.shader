Shader " Self-Illumin" {
	Properties {
		_Color ("Main Color", Color) = (1,1,1,1)
		_MainTex ("Base (RGB)", 2D) = "ah64rotor1"
	}

	Category {
		SubShader {
			Color [_Color]
			Pass {
				Lighting Off
				SeperateSpecular On
				SetTexture [_MainTex] {Combine texture * primary, texture * primary}
			}
		}
	}
}
