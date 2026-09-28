Shader "GooBall/Monte clouds" {
	Properties {
		_TintColor ("Tint Color", Color) = (1,1,1,1)
		_MainTex ("Particle Texture", 2D) = "dummy.jpg"
	}
	
	SubShader {
//		Tags { "Queue" = "Transparent" }
		Cull Off
		Lighting Off
		Fog { color (0,0,0,0)	}
		Color (1,1,1,1)
		ColorMask RGB
		Blend SrcAlpha OneMinusSrcAlpha
		Pass {
			AlphaTest Greater .9
			SetTexture [_MainTex] {
				constantColor [_TintColor]
				combine constant * texture DOUBLE, constant *  texture DOUBLE
			}
			SetTexture [_MainTex] {
				combine previous * primary
			}
		}
		Pass {
			ZWrite Off
			AlphaTest LEqual .9
			SetTexture [_MainTex] {
				constantColor [_TintColor]
				combine constant * texture DOUBLE, constant *  texture DOUBLE
			}
			SetTexture [_MainTex] {
				combine previous * primary
			}
		}
	}
}
