# PWV3 D10-F02 Global-repeat owner decision — Option A

Date: 2026-10-04
Workstream: `change-workflow-successor-product`
Subject: `workflow-successor-product@6`
Source review attempt: `D10-OP-DEFREV-A01`
Source finding: `D10-F02`
Status: **OWNER DECISION — OPTION A**

The human owner selected **Option A — an explicit same-binding Global repeat remains legal until the durable final-integration intent/cut begins**.

## Accepted semantics

After an applicable Global CLEAR, fresh terminal acceptance proceeds automatically and no routine CONTINUE / RUN OP AGAIN gate is created.

Until final integration has durably begun, the owner may explicitly request one further same-binding Global. That request is a durable, single-use semantic transition which must:
- revalidate the exact frozen candidate and acceptance/coverage binding;
- supersede for forward authority the predecessor CLEAR and any pending or already accepted terminal-acceptance result derived from it;
- preserve all superseded evidence as immutable history only;
- establish and positively read back exactly one successor Global attempt frontier on the same applicable binding;
- make that successor Global frontier the sole qualification-current frontier for forward advancement;
- block final integration until the successor Global reaches an applicable advancing result and a fresh applicable terminal acceptance completes.

Once the durable final-integration intent/cut has begun, a same-binding Global repeat is no longer legal in that qualification epoch.

Recovery must reconstruct only the newest applicable current frontier. No predecessor CLEAR, superseded terminal-acceptance attempt/result, or stale success may regain forward authority.

This decision is bounded authority for repair of D10-F02 and does not create a routine post-Global user gate.
