{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "busybeaver.name" -}}
{{- default .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "busybeaver.fullname" -}}
{{- $name := default .Chart.Name -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "busybeaver.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Common labels
*/}}
{{- define "busybeaver.labels" -}}
{{ include "busybeaver.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ include "busybeaver.chart" . }}
{{- end -}}

{{/*
Selector labels
*/}}
{{- define "busybeaver.selectorLabels" -}}
app: webapp
environment: {{ .Values.environment }}
app.kubernetes.io/name: {{ include "busybeaver.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/*
Environment Variables
*/}}
{{- define "busybeaver.env_vars" }}
{{- if eq .Values.environment "production" }}
- name: ENVIRONMENT
  value: {{ .Values.environment }}
- name: IN_PRODUCTION
  value: "1"
{{- end }}
- name: PYTHONPATH
  value: .
- name: FLASK_APP
  value: /app/busy_beaver/__init__.py
- name: SECRET_KEY
  valueFrom:
    secretKeyRef:
      name: {{ .Values.secretName }}
      key: secret-key
- name: SENTRY_DSN
  valueFrom:
    secretKeyRef:
      name: {{ .Values.secretName }}
      key: sentry-dsn
# infrastructure
- name: DATABASE_URI
  valueFrom:
    secretKeyRef:
      name: {{ .Values.secretName }}
      key: db-uri
- name: REDIS_URI
  valueFrom:
    secretKeyRef:
      name: {{ .Values.secretName }}
      key: cache-uri
# integrations
# oauth lib
- name: OAUTHLIB_INSECURE_TRANSPORT
  value: "1"
- name: OAUTHLIB_RELAX_TOKEN_SCOPE
  value: "1"
# slack
- name: SLACK_CLIENT_ID
  valueFrom:
    secretKeyRef:
      name: {{ .Values.secretName }}
      key: slack-client-id
- name: SLACK_CLIENT_SECRET
  valueFrom:
    secretKeyRef:
      name: {{ .Values.secretName }}
      key: slack-client-secret
- name: SLACK_BOTUSER_OAUTH_TOKEN
  valueFrom:
    secretKeyRef:
      name: {{ .Values.secretName }}
      key: slack-botuser-oauth-token
- name: SLACK_SIGNING_SECRET
  valueFrom:
    secretKeyRef:
      name: {{ .Values.secretName }}
      key: slack-signing-secret
# meetup
- name: MEETUP_API_KEY
  valueFrom:
    secretKeyRef:
      name: {{ .Values.secretName }}
      key: meetup-api-key
# github
- name: GITHUB_APP_CLIENT_ID
  valueFrom:
    secretKeyRef:
      name: {{ .Values.secretName }}
      key: github-client-id
- name: GITHUB_APP_CLIENT_SECRET
  valueFrom:
    secretKeyRef:
      name: {{ .Values.secretName }}
      key: github-client-secret
- name: GITHUB_OAUTH_TOKEN
  valueFrom:
    secretKeyRef:
      name: {{ .Values.secretName }}
      key: github-oauth-token
- name: GITHUB_SIGNING_SECRET
  valueFrom:
    secretKeyRef:
      name: {{ .Values.secretName }}
      key: github-signing-secret
# twitter
- name: TWITTER_ACCESS_TOKEN_SECRET
  valueFrom:
    secretKeyRef:
      name: {{ .Values.secretName }}
      key: twitter-access-token-secret
- name: TWITTER_ACCESS_TOKEN
  valueFrom:
    secretKeyRef:
      name: {{ .Values.secretName }}
      key: twitter-access-token
- name: TWITTER_CONSUMER_KEY
  valueFrom:
    secretKeyRef:
      name: {{ .Values.secretName }}
      key: twitter-consumer-key
- name: TWITTER_CONSUMER_SECRET
  valueFrom:
    secretKeyRef:
      name: {{ .Values.secretName }}
      key: twitter-consumer-secret
{{- end }}
