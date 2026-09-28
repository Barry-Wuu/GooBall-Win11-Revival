Shader "Particles/Billboard" {
	Properties {
		_TintColor ("Tint Color", Color) = (1,1,1,1)
		_MainTex ("Particle Texture", 2D) = "dummy.jpg"
	}
	
	SubShader {
		Tags { "Queue" = "Background" }
		Cull Off
		Lighting Off
		AlphaTest Greater .5
		ColorMask RGB
		Blend SrcAlpha OneMinusSrcAlpha
		Pass {
			SetTexture [_MainTex] {
				constantColor [_TintColor]
				combine constant * texture, texture
			}
		}
	}
}
