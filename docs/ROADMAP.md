
# Table of Contents

1.  [Python3](#orgba25b9f)
2.  [Python2](#orgdb2a1c4)
3.  [Rust](#orgadb2767)

The roadmap is split into three sub-tasks: Python3, Python2, and Rust. The Python3 sub-task should be the longest as that also includes refactoring the ACCRa codebase to support the language components.

The **ACHIEVEMENT** sections reflect capabilities that should be integrated in the ACCRa codebase by the **DUE DATE** (unless specified otherwise in **COMMENTS**.


<a id="orgba25b9f"></a>

# Python3

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-right" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">ACHIEVEMENT</th>
<th scope="col" class="org-right">DUE DATE</th>
<th scope="col" class="org-left">COMMENTS</th>
<th scope="col" class="org-left">STATUS</th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left">Installation of interpreter.</td>
<td class="org-right">2026-09-29</td>
<td class="org-left">Minor version should be accounted for.</td>
<td class="org-left">INTEGRATION</td>
</tr>

<tr>
<td class="org-left">Installation of Python3 dependencies.</td>
<td class="org-right">2026-09-29</td>
<td class="org-left">&nbsp;</td>
<td class="org-left">INTEGRATION</td>
</tr>

<tr>
<td class="org-left">Building Python3 environment.</td>
<td class="org-right">2026-10-02</td>
<td class="org-left">&nbsp;</td>
<td class="org-left">INTEGRATION</td>
</tr>

<tr>
<td class="org-left">Reflecting build process in DB.</td>
<td class="org-right">2026-10-09</td>
<td class="org-left">Requires refactoring DB schema.</td>
<td class="org-left">STARTED</td>
</tr>

<tr>
<td class="org-left">Migrate Prolog reasoning to Python3 component.</td>
<td class="org-right">2026-10-15</td>
<td class="org-left">&nbsp;</td>
<td class="org-left">STARTED</td>
</tr>
</tbody>
</table>


<a id="orgdb2a1c4"></a>

# Python2

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-right" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">ACHIEVEMENT</th>
<th scope="col" class="org-right">DUE DATE</th>
<th scope="col" class="org-left">COMMENTS</th>
<th scope="col" class="org-left">STATUS</th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left">Installation of interpreter.</td>
<td class="org-right">2026-10-18</td>
<td class="org-left">&nbsp;</td>
<td class="org-left">STARTED</td>
</tr>

<tr>
<td class="org-left">Installation of Python2 dependencies.</td>
<td class="org-right">2026-10-18</td>
<td class="org-left">&nbsp;</td>
<td class="org-left">STARTED</td>
</tr>

<tr>
<td class="org-left">Building Python2 environment.</td>
<td class="org-right">2026-10-18</td>
<td class="org-left">&nbsp;</td>
<td class="org-left">STARTED</td>
</tr>

<tr>
<td class="org-left">Python2 reasoning.</td>
<td class="org-right">2026-10-18</td>
<td class="org-left">Reuse Prolog rules from ACCRa.</td>
<td class="org-left">&nbsp;</td>
</tr>
</tbody>
</table>


<a id="orgadb2767"></a>

# Rust

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-right" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">ACHIEVEMENT</th>
<th scope="col" class="org-right">DUE DATE</th>
<th scope="col" class="org-left">COMMENTS</th>
<th scope="col" class="org-left">STATUS</th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left">Installation of Rust compiler.</td>
<td class="org-right">2026-10-24</td>
<td class="org-left">Take into account <code>stable</code> vs <code>unstable</code>.</td>
<td class="org-left">&nbsp;</td>
</tr>

<tr>
<td class="org-left">Installation of cargo dependencies.</td>
<td class="org-right">2026-10-24</td>
<td class="org-left">&nbsp;</td>
<td class="org-left">&nbsp;</td>
</tr>

<tr>
<td class="org-left">Building Rust environment.</td>
<td class="org-right">2026-10-24</td>
<td class="org-left">&nbsp;</td>
<td class="org-left">&nbsp;</td>
</tr>

<tr>
<td class="org-left">Rust reasoning.</td>
<td class="org-right">???</td>
<td class="org-left">Depends on how well we can write Prolog rules.</td>
<td class="org-left">&nbsp;</td>
</tr>
</tbody>
</table>

