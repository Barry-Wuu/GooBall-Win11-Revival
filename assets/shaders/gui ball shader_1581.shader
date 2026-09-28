Shader "GUI/ball"
{
	Properties {
		_MainTex ("Particle Texture", 2D) = "dummy.jpg"
	}
	
	SubShader {
		Tags {
			"Queue" = "Background"
		}
		Cull back
		Lighting Off
		zwrite off
		Fog { Mode Off }
		Ztest always
		Blend SrcAlpha OneMinusSrcAlpha
		Pass {
			SetTexture [_MainTex] {
				combine texture
			}
		}
	}
}
