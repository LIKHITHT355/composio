# Composio Usage Plan & Architecture

## Overview
Composio bridges AI agents with 1500+ external tools, toolkits, and authentications. In this automated research system, Composio is leveraged for:
1. **Toolkit & MCP Catalog Cross-Referencing**:
   Checking whether an application already has official or community toolkit coverage in Composio (`composio` toolsets).
2. **MCP Integration**:
   Utilizing Composio's managed MCP server capabilities (`composio.create(..., mcp=True)`) or tool discovery meta-tools where applicable.
3. **Automated Verification Execution**:
   Executing search and retrieval through Composio-managed toolkits (or integrated search actions) when verifying API documentation and endpoints.

## Real SDK Interface Details (Verified from Official Composio Docs)
- **Primary Package**: `composio-core` / `composio`
- **Class / Client**:
  ```python
  from composio import Composio, App, Action

  # Client initialization
  client = Composio(api_key=COMPOSIO_API_KEY)

  # Check apps in catalog
  # apps = client.apps.get()
  # actions = client.actions.get(app=App.GITHUB)
  ```
- **MCP Sessions**:
  ```python
  session = client.create(
      user_id="research_agent",
      toolkits=["search", "web_crawler"],
      mcp=True
  )
  ```

## Honest Boundary: Where Humans vs. Agents Act
1. **Agent Domain**:
   - Querying search engines & public documentation.
   - Parsing OpenAPI specs, developer portals, rate limit sections.
   - Determining auth schemes (OAuth2 vs API Key vs Session Token) and self-serve gating status.
   - Cross-referencing against Composio's catalog.
2. **Human Touchpoint Boundary**:
   - Hand-checking a sample set (e.g. 20 apps) for ground truth calibration.
   - Reviewing apps where vendor documentation is protected behind contact-sales or private partner portals.
   - Adjudicating ambiguous cases where an app has an unofficial reverse-engineered API vs an official developer platform.
