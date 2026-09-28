Shader " VertexLit nofog" {
	Properties {
		_Color ("Main Color", Color) = (1,1,1,1)
		_Emission ("Emmisive Color", Color) = (0,0,0,0)
		_Shininess ("Shininess", range (0,1)) = 0.1
		_Highlight ("Highlight size", range (0,64)) = 30
		_MainTex ("Base (RGB)", 2D) = "ah64rotor1"
	}

	Category {
		SubShader {
			Material {
				Diffuse [_Color]
				Specular ([_Shininess], [_Shininess], [_Shininess], 0)
				Shininess [_Highlight]
				Emission [_Emission] //[_PPLAmbient]
			}
			Pass {
				Fog { Mode Off }
				Lighting On
				SeperateSpecular On
				SetTexture [_MainTex] {Combine texture * primary DOUBLE, texture * constant constantColor [_Color]}
			}
		}
	}
}
