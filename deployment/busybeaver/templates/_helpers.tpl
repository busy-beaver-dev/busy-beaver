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
- name: PYTHONPATH
  value: .
- name: FLASK_APP
  value: /app/busy_beaver/__init__.py
- name: DATABASE_URI
  valueFrom:
    secretKeyRef:
      name: busybeaver-staging
      key: db-uri
- name: REDIS_URI
  valueFrom:
    secretKeyRef:
      name: busybeaver-staging
      key: cache-uri
- name: SENTRY_DSN
  valueFrom:
    secretKeyRef:
      name: busybeaver-staging
      key: sentry-dsn
# integrations
# slack
- name: SLACK_CLIENT_ID
  valueFrom:
    secretKeyRef:
      name: busybeaver-staging
      key: slack-client-id
- name: SLACK_CLIENT_SECRET
  valueFrom:
    secretKeyRef:
      name: busybeaver-staging
      key: slack-client-secret
- name: SLACK_BOTUSER_OAUTH_TOKEN
  valueFrom:
    secretKeyRef:
      name: busybeaver-staging
      key: slack-botuser-oauth-token
- name: SLACK_SIGNING_SECRET
  valueFrom:
    secretKeyRef:
      name: busybeaver-staging
      key: slack-signing-secret
# meetup
- name: MEETUP_API_KEY
  valueFrom:
    secretKeyRef:
      name: busybeaver-staging
      key: meetup-api-key
# github
- name: GITHUB_APP_CLIENT_ID
  valueFrom:
    secretKeyRef:
      name: busybeaver-staging
      key: github-client-id
- name: GITHUB_APP_CLIENT_SECRET
  valueFrom:
    secretKeyRef:
      name: busybeaver-staging
      key: github-client-secret
- name: GITHUB_OAUTH_TOKEN
  valueFrom:
    secretKeyRef:
      name: busybeaver-staging
      key: github-oauth-token
- name: GITHUB_SIGNING_SECRET
  valueFrom:
    secretKeyRef:
      name: busybeaver-staging
      key: github-signing-secret
# twitter
- name: TWITTER_ACCESS_TOKEN_SECRET
  valueFrom:
    secretKeyRef:
      name: busybeaver-staging
      key: twitter-access-token-secret
- name: TWITTER_ACCESS_TOKEN
  valueFrom:
    secretKeyRef:
      name: busybeaver-staging
      key: twitter-access-token
- name: TWITTER_CONSUMER_KEY
  valueFrom:
    secretKeyRef:
      name: busybeaver-staging
      key: twitter-consumer-key
- name: TWITTER_CONSUMER_SECRET
  valueFrom:
    secretKeyRef:
      name: busybeaver-staging
      key: twitter-consumer-secret
{{- end }}
