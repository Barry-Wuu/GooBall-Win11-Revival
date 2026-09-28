Shader "Particles/Nofog Blend" {
	Properties {
		_TintColor ("Tint Color", Color) = (1,1,1,1)
		_MainTex ("Particle Texture", 2D) = "dummy.jpg"
	}
	
	SubShader {
		Tags { "Queue" = "Transparent" }
		Cull Off
		Lighting Off
		zwrite off
		Fog { Mode Off	}
		ColorMask RGB
		Blend SrcAlpha OneMinusSrcAlpha
		Pass {
			SetTexture [_MainTex] {
				constantColor [_TintColor]
				combine constant * texture
			}
		}
	}
}
