Shader "GooBall/Rocket burns" {
	Properties {
		_Color ("Main Color", Color) = (1,1,1,1)
		_Shininess ("Shininess", range (0,1)) = 0.1
		_Highlight ("Highlight size", range (0,64)) = 30
		_MainTex ("Base (RGB)", 2D) = "ah64rotor1"
	}

	Category {
		ZWrite Off
		Tags { "Queue" = "Transparent" }
		Color [_Color]
		Offset -3, -3
		SubShader {
			Pass {
				Blend Zero SrcColor
				SetTexture [_MainTex] {Combine texture * primary}
			}
		}
	}
}


