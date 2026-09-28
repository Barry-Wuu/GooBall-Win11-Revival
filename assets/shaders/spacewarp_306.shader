// Glass with fresnel reflection & transparency...
// Tested on: ATI Radeon Mobility

SHADER "FX/Spacewarp" { 
	Properties {
		_Color ("Main Color(RGB) Shine (A)", COLOR)  = ( 0 , .1 , 0 , .1)
		_EdgeColor ("Edge Color(RGB) Shine (A)", COLOR)  = ( 0 , .1 , 0 , .1)
		_distort ("Distortion", Range (0,1)) = .1
		_MainTex ("texture", 2D) = "fresnel.png"
	}

	// ARB_FP shader
	SubShader { 
		Tags {"Queue" = "Transparent" }
		Cull Off
		Blend SrcColor OneMinusSrcAlpha
		ZWrite Off
		Fog { Mode Off}
		Pass {

Program "" {
SubProgram {
  bind "vertex", ATTR0
  bind "texcoord", ATTR1
  Local 48, [_EdgeCol]
  Local 2, [_CosTime]
  Local 1, [_SinTime]

  "!!ARBvp1.0
  PARAM c49 = { 0, 1, 0, 0 };
  ATTRIB v1 = vertex.attrib[1];
  ATTRIB v0 = vertex.attrib[0];
  PARAM c48 = program.local[48];
  PARAM c2 = program.local[2];
  PARAM c1 = program.local[1];
  PARAM s259[4] = { state.matrix.mvp };
  	DP4 result.position.x, s259[0], v0;
  	DP4 result.position.y, s259[1], v0;
  	DP4 result.position.z, s259[2], v0;
  	DP4 result.position.w, s259[3], v0;
  	MOV result.texcoord[0].yzw, v1;
  	ADD result.texcoord[0].x, v1.x, c1.y;
  	MOV result.texcoord[1].xzw, v1;
  	ADD result.texcoord[1].y, v1.y, c2.y;
  	MOV result.color.front.primary, c48;
  END
  	"
}

}

Program "" {
SubProgram {
  Local 1, ([_distort],0,0,0)
  Local 2, [_Color]
  Local 0, [_EdgeColor]
  SetTexture [_MainTex]
  SetTexture [_MainTex2]

  "!!ARBfp1.0
  PARAM u1 = program.local[1];
  PARAM u2 = program.local[2];
  PARAM u0 = program.local[0];
  TEMP R0;
  TEMP R1;
  TEMP H0;
  TEMP H1;
  TEX R0.x, fragment.texcoord[0], texture[0], 2D;
  TEX R1.x, fragment.texcoord[1], texture[0], 2D;
  MOV H0.xy, R0.x;
  MOV H0.zw, R1.x;
  MUL R0, H0, u1.x;
  MOV H0, u0;
  ADD H0, u2, -H0;
  ADD R1.xy, R0.zwzz, fragment.texcoord[0];
  TEX R1.x, R1, texture[0], 2D;
  ADD R0.xy, R0, fragment.texcoord[1];
  TEX R0.x, R0, texture[0], 2D;
  ADD H1.x, R0.x, R1.x;
  MAD result.color, H1.x, H0, u0;
  END
  	"
}

}
			Color [_EdgeColor]
			SetTexture [_MainTex] {combine texture alpha}
			SetTexture [_MainTex] {
				constantColor [_Color]
				combine constant lerp (previous) primary
			}
		}
	}

	// GeforceTI shader
	SubShader {
		Tags {"Queue" = "Transparent" }
		Cull Off
		Blend One OneMinusSrcColor
		ZWrite Off
		Fog { Mode Off}
		Pass {
			SetTexture [_MainTex] {
				constantColor [_Color]
				combine constant * texture alpha
			}
			SetTexture [_MainTex] {
				combine texture alpha + previous 					}
			SetTexture [_MainTex] {
				constantColor [_Color]
				combine constant lerp (previous) primary
			}
		}	
	}

	// Geforce4MX shader
	SubShader {
		Tags {"Queue" = "Transparent" }
		Cull Off 
		Blend One OneMinusSrcColor
		ZWrite Off
		Fog { Mode Off}
		Pass {
			SetTexture [_MainTex] {
				constantColor [_Color]
				combine constant * texture alpha + primary
			}
			SetTexture [_MainTex] {
				constantColor [_Color]
				combine constant * texture alpha, texture * previous 			}
		}	
	}
	Fallback "Particles/LightFlare", 1
}