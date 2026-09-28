Shader "Particles/Additive" {
	Properties {
		_TintColor ("Tint Color", Color) = (1,1,1,1)
		_MainTex ("Particle Texture", 2D) = "dummy.jpg" {}
	}
	
	SubShader {
		Tags { "Queue" = "Transparent" }
		cull off
		Lighting Off
		zwrite off
		Blend ONE ONE
		Fog { Color (0,0,0,0)	}
		color (1,1,1,1)
		Pass {
			SetTexture [_MainTex] {
				constantColor [_TintColor]
				combine constant * texture DOUBLE, constant
			}
			SetTexture [_MainTex] {
				combine previous * primary, constant
			}
		}
	}
}