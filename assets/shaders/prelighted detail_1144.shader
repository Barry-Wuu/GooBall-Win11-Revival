Shader "Water/Prelight detail" {
	Properties {
		_Color ("Color", Color) = (1,1,1,1)
		_FCol ("Fog Color", Color) = (1,1,1,1)
		_MainTex ("Particle Texture", 2D) = "dummy.jpg" {}
		_DetailTex ("Falloff texture", 2D) = "" {}
	}
	
	SubShader {
		Pass {
			Fog {
				Color [_FCol]
			}
			SetTexture [_MainTex] {
				constantColor [_Color]
				combine constant * texture
			}
			SetTexture [_DetailTex] {
				constantColor [_Color]
				combine texture * previous DOUBLE, constant
			}
			SetTexture [_DetailTex] {
				constantColor [_Color]
				combine previous
			}
		}
	}
	SubShader {
		Pass {
			Fog {
				Color [_FCol]
			}
			SetTexture [_MainTex] {
				constantColor [_Color]
				combine constant * texture
			}
			SetTexture [_DetailTex] {
				constantColor [_Color]
				combine texture * previous DOUBLE, constant
			}
		}
	}
}