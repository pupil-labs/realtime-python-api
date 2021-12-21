**************
Under The Hood
**************

This guide explains how the Pupil Labs' Realtime API works on the wire and how this
client library abstracts away some of the complexities of ther underlying protocols.

REST API
========

1. Start/stop/cancel recordings
2. Send events
3. Get status
    1. ip address, battery, storage
    2. Sensors
    3. Status changes (e.g. new sensors; via web socket connection)

RTSP Streaming API
==================

1. High level overview over RTSP, RTP, and RTCP
2. How to get stream entry points from status call
3. Receive gaze
    1. Without timestamps (explain how to decode RTP payload)
    2. With relative timestamps (explain how to get timestamps from RTP headers)
    3. With wall clock timestamps (explain hot to sync relative ts to wall clock ts using RTCP packets)
4. Receive video
    1. Using OpenCV without timestamps
    2. Using PyAV (and reusing  wall clock timestamps from 3.3.3)

Local network discovery via Bonjour
===================================
