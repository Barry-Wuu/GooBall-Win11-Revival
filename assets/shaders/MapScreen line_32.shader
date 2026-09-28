Shader "GooBall/MapScreen Line" {
	Properties {
		_TintColor ("Tint Color", Color) = (1,1,1,1)
		_MainTex ("Particle Texture", 2D) = "dummy.jpg"
	}
	
	SubShader {
		Tags { "Queue" = "Transparent" }
		Cull Off
		Lighting Off
		AlphaTest Greater .1
		ZTest always
		Fog { color (0,0,0,0)	}
		Blend SrcAlpha OneMinusSrcAlpha
		ColorMask RGB
		Pass {
			SetTexture [_MainTex] {
				constantColor [_TintColor]
				combine constant DOUBLE, constant *  texture DOUBLE
			}
		/*	SetTexture [_MainTex] {
				combine previous * primary
			}*/
		}
	}
}
