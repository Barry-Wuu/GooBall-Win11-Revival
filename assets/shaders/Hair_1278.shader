Shader "GooBall/Evil Hair" {
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
		SubShader {
			Pass {
				Blend Zero SrcColor
				Cull Off
				SetTexture [_MainTex] {Combine one - texture alpha * primary DOUBLE}
//				SetTexture [_MainTex] {Combine texture * primary DOUBLE}
//				SetTexture [_MainTex] {Combine texture * primary DOUBLE}
			}
		}
		SubShader {
			Pass {
				Blend SrcAlpha OneMinusSrcAlpha
				Cull Off
				SetTexture [_MainTex] {Combine texture * primary DOUBLE}
				SetTexture [_MainTex] {Combine texture * primary DOUBLE}
			}
		}
	}
}
