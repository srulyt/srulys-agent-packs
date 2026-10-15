# Smart Alerts: Alert Routing Brief

## Executive Summary

In today's fast-paced landscape, on-call engineers are drowning in noise. Smart Alerts is a game-changing, cutting-edge capability that seamlessly routes each alert to the team that owns the affected service. We request approval to staff two engineers for Q3 to build Smart Alerts.

## Problem

**Current state**

Every alert from the monitoring platform pages the central operations rotation. In Q1, the rotation received 4,100 pages; 62% were reassigned to another team by hand (ops ticket export, Q1).

**Impact**

Median time to the right owner is 38 minutes (ops ticket export, Q1). See the [incident dashboard](https://example.com/incidents) for details.

## Proposal

It's worth noting that Smart Alerts reads the existing service ownership catalog and attaches the owning team to each alert at creation time. Alerts for services without an owner continue to page the central rotation. Smart alerts do not change alert thresholds.

## Decision Ask

Approve two engineers for Q3 (about 10 engineer-weeks each) to build Smart Alerts. Without approval, the central rotation keeps absorbing the reassignment load through Q4.
