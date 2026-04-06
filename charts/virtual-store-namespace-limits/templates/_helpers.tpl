{{- define "virtual-store-namespace-limits.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "virtual-store-namespace-limits.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- include "virtual-store-namespace-limits.name" . -}}
{{- end -}}
{{- end -}}
