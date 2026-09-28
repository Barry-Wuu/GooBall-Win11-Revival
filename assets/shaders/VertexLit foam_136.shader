Shader "Water/foam" {
	Properties {
		_Color ("Main Color", Color) = (1,1,1,1)
		_Shininess ("Shininess", range (0,1)) = 0.1
		_Highlight ("Highlight size", range (0,64)) = 30
		_scale ("Scale", Range (.3,1)) = 1
		_MainTex ("Base (RGB)", 2D) = "ah64rotor1" 
	}

	Category {
		Tags { "Queue" = "Foam" }
		SubShader {
			Pass {

Program "" {
SubProgram {
  bind "vertex", ATTR0
  bind "texcoord", ATTR1
  Local 5, [_Color]
  Local 6, [_waveTime]

  "!!ARBvp1.0
  PARAM c[8] = { { 2, 1, 3, 0.30000001 },
  		state.matrix.mvp,
  		program.local[5..6],
  		{ 0.2, 0.60000002 } };
  TEMP R0;
  TEMP R1;
  TEMP R2;
  MOV R0.x, c[0].w;
  MUL R0, c[6], R0.x;
  ADD R1, R0, c[0].w;
  MUL R0, vertex.attrib[1], c[0].yzyy;
  ADD R2.x, R1, c[7];
  MUL R1.x, R1, c[7].y;
  RCP R2.x, R2.x;
  MAD result.texcoord[0].x, R0, R2, -R1;
  ADD R1.x, R1.y, c[7];
  MUL R1.y, R1, c[7];
  RCP R1.x, R1.x;
  MAD result.texcoord[1].x, R0, R1, -R1.y;
  ADD R1.x, R1.z, c[7];
  MUL R1.y, R1.z, c[7];
  RCP R1.x, R1.x;
  MAD result.texcoord[2].x, R0, R1, -R1.y;
  ADD R0.x, -R1.w, R0.y;
  ADD result.texcoord[0].y, R0, -R1.w;
  ADD result.texcoord[1].y, R0.x, -c[0];
  ADD result.texcoord[2].y, R0.x, -c[0].x;
  MUL R0.x, -vertex.attrib[1], c[0];
  ADD R1.w, R0.x, c[0].x;
  DP4 R0.xy, vertex.attrib[0], c[3];
  MOV R1.xyz, c[5];
  MUL result.color, R1, c[5];
  MOV result.texcoord[0].zw, R0;
  MOV result.texcoord[1].zw, R0;
  MOV result.texcoord[2].zw, R0;
  MOV result.position.z, R0.y;
  MOV result.fogcoord.x, R0;
  DP4 result.position.w, vertex.attrib[0], c[4];
  DP4 result.position.y, vertex.attrib[0], c[2];
  DP4 result.position.x, vertex.attrib[0], c[1];
  END
  # 33 instructions, 3 R-regs
  	"
}

}
				ZWrite Off
				Offset -4, -4
				Blend SrcAlpha OneMinusSrcAlpha
				ColorMask RGB
				SetTexture [_MainTex] {Combine texture * primary }
				SetTexture [_MainTex] {Combine texture + previous, texture * primary + previous}
				SetTexture [_MainTex] {Combine texture + previous, texture * primary + previous}
			}
		}
	}
	Category {
		Tags { "Queue" = "Overlay" }
		SubShader {
			Pass {
				ZWrite Off
				Offset -2, -2
				Blend Zero One
				ColorMask RGB
			}
		}
	}
}
