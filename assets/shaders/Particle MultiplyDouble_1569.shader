Shader "Particles/Multiply 2x"
{
	Properties {
		_MainTex ("Particle Texture", 2D) = "dummy.jpg"
	}
	
	SubShader {
		Tags {
			"Queue" = "Transparent"
		}
		Cull Off
		Lighting Off
		zwrite off
		Blend DstColor SrcColor
		Fog { Color (.5, .5, .5) }
		Pass {
			SetTexture [_MainTex] {
				constantColor (.5, .5, .5, .5)
				combine texture lerp (primary)constant 
			}
		}
	}
}