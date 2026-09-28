Shader "Particles/Alpha Blend" {
	Properties {
		_TintColor ("Tint Color", Color) = (1,1,1,1)
		_MainTex ("Particle Texture", 2D) = "dummy.jpg"
	}
	
	SubShader {
		Tags { "Queue" = "Transparent" }
		Cull Off
		Lighting Off
		zwrite off
		Fog { color (0,0,0,0)	}
		AlphaTest Greater .01
		Blend SrcAlpha OneMinusSrcAlpha
		Pass {
			SetTexture [_MainTex] {
				constantColor [_TintColor]
				combine constant DOUBLE, constant *  texture
			}
			/*SetTexture [_MainTex] {
				combine previous * primary
			}*/
		}
	}
}
