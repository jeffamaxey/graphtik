.. _arch:

============
Architecture
============


.. default-role:: term

.. include:: index.rst
    :start-after: .. math-overview-start
    :end-before: .. math-overview-end

.. glossary::

    compute
    computation
    phase

        The definition & execution of `pipeline`\s happens in 3 phases:

        - `composition`
        - `planning`
        - `execution`

        |v440-flowchart|

        ... it is constrained by these IO data-structures:

        - `operation`\(s)
        - `dependencies <dependency>` (`needs` & `provides`)
        - given `inputs`
        - asked `outputs`

        ... populates these low-level data-structures:

        - `network` (COMPOSE time)
        - `execution dag` (COMPILE time)
        - `execution steps` (COMPILE time)
        - `solution` (EXECUTE time)

        ... and utilizes these main classes:

        .. autosummary::

            graphtik.fnop.FnOp
            graphtik.pipeline.Pipeline
            graphtik.planning.Network
            graphtik.execution.ExecutionPlan
            graphtik.execution.Solution

        ... plus those for `plotting`:

        .. autosummary::

            graphtik.plot.Plotter
            graphtik.plot.Theme

    compose
    composition
        The `phase` where `operation`\s are constructed and grouped
        into `pipeline`\s and corresponding `network`\s based on their `dependencies
        <dependency>`.

        .. Tip::
            - Use :func:`.operation` factory to construct :class:`.FnOp`
              instances (a.k.a. operations).
            - Use :func:`.compose()` factory to build :class:`.Pipeline`
              instances (a.k.a. pipelines).

    recompute
        There are 2 ways to feed the `solution` back into the same `pipeline`:

        * by reusing the pre-compiled `plan` (coarse-grained), or
        * by using the ``compute(recalculate_from=...)`` argument (fine-grained),

        as described in :ref:`recompute` tutorial section.

        .. attention::
            This feature is not well implemented (e.g. ``test_recompute_NEEDS_FIX()``),
            neither thoroughly tested.

    combine pipelines
        When `operation`\s and/or `pipeline`\s are `compose`\d together, there are
        two ways to combine the operations contained into the new pipeline:
        `operation merging` (default) and `operation nesting`.

        They are selected by the ``nest`` parameter of :func:`.compose()` factory.

    operation merging
        The default method to `combine pipelines`, also applied when simply merging `operation`\s.

        Any identically-named operations override each other,
        with the operations added earlier in the ``.compose()`` call
        (further to the left) winning over those added later (further to the right).

        :seealso: :ref:`operation-merging`

    operation nesting
        The elaborate method to `combine pipelines` forming *clusters*.

        The original pipelines are preserved intact in "isolated" clusters,
        by prefixing the names of their operations (and optionally data)
        by the name of the respective original pipeline that contained them
        (or the user defines the renames).

        :seealso: :ref:`operation-nesting`, :func:`.compose`, :class:`.RenArgs`,
            :func:`.nest_any_node()`, :func:`.dep_renamed()`, :attr:`.PlotArgs.clusters`,
            :ref:`hierarchical-data` (example).

    compile
    compilation
    planning
        The `phase` where the :class:`.Network` creates a new `execution plan`
        by `pruning` all `graph` nodes into a subgraph `dag`, and  deriving
        the `execution steps`.

    execute
    execution
    sequential
        The `phase` where the `plan` derived from a `pipeline` calls the underlying
        functions of all `operation`\s contained in its `execution steps`,
        with `inputs`/`outputs` taken/written to the `solution`.

        Currently there are 2 ways to execute:

        - *sequential*
        - (deprecated) `parallel`, with a :class:`multiprocessing.pool.ProcessPool`

        Plans may abort their execution by setting the `abort run` global flag.

    network
    graph
        A :attr:`.Network.graph` of `operation`\s linked by their `dependencies <dependency>` implementing a `pipeline`.

        During `composition`, the nodes of the graph are connected by repeated calls
        of :meth:`.Network._append_operation()` within ``Network`` constructor.

        During `planning` the *graph* is `prune`\d based on the given `inputs`,
        `outputs` & `node predicate` to extract the `dag`, and it is ordered,
        to derive the `execution steps`, stored in a new `plan`, which is then
        cached on the ``Network`` class.


    plan
    execution plan
        Class :class:`.ExecutionPlan` perform the `execution` phase which contains
        the `dag` and the `steps`.

        `compile`\ed *execution plans* are cached in :attr:`.Network._cached_plans`
        across runs with (`inputs`, `outputs`, `predicate`) as key.

    solution
        A map of `dependency`-named values fed to/from the `pipeline` during `execution`.

        It feeds operations with `inputs`, collects their `outputs`,
        records the *status* of executed or `canceled operation`\s,
        tracks any `overwrite`\s, and applies any `eviction`\s, as orchestrated
        by the `plan`.

        A new :class:`.Solution` instance is created either internally
        by :meth:`.Pipeline.compute()` and populated with user-inputs, or must be
        created externally with those values and fed into the said method.

        The results of the last operation executed "win" in the `layer`\s,
        and the base (least precedence) is the user-inputs given when the execution
        started.

        Certain values may be extracted/populated with `accessor`\s.

    layer
    solution layer
        The `solution` class inherits :class:`~collections.ChainMap`,
        to store the actual `outputs` of each  executed `operation` in a separate dictionary
        (+1 for user-inputs).

        When layers are disabled, the `solution` populates the passed-in `inputs`
        and stores in *layers* just the keys of *outputs* produced.

        The layering, by default, is disabled if a `jsonp` `dependency` exists in the `network`,
        and :func:`.set_layered_solution` `configurations` has not been set,
        nor has the respective parameter been given to methods
        :meth:`~.FnOp.compute()`/:meth:`~.ExecutionPlan.execute()`.

        If disabled, `overwrite`\s are lost, but are marked as such.

        .. hint::

            Combining `hierarchical data` with *per-operation layers* in solution
            leads to duplications of container nodes in the data tree.
            To retrieve the complete solution, merging of `overwritten <overwrite>`
            nodes across the layers would then be needed.

    overwrite
        `solution` values written by more than one `operation`\s in the respective `layer`,
        accessed by :attr:`.Solution.overwrites` attribute
        (assuming that *layers* have not been disabled e.g. due to `hierarchical data`,
        in which case, just the `dependency` names of the `outputs` actually produced
        are stored).

        Note that `sideffected` outputs always produce an *overwrite*.

        *Overwrites* will not work for If `evicted <eviction>` outputs.

    prune
    pruning
        A subphase of `planning` performed by method :meth:`.Network._prune_graph()`,
        which extracts a subgraph `dag` that does not contain any `unsatisfied operation`\s.

        It topologically sorts the `graph`, and *prunes* based on given `inputs`,
        asked `outputs`, `node predicate` and `operation` `needs` & `provides`.

    unsatisfied operation
        The core of `pruning` & `rescheduling`, performed by
        :func:`.planning.unsatisfied_operations()` function, which collects
        all `operation`\s with unreachable `dependencies <dependency>`:

        - they have `needs` that do not correspond to any of the given `inputs` or
          the intermediately `compute`\d `outputs` of the `solution`;
        - all their `provides` are NOT needed by any other operation, nor are asked
          as *outputs*.

    dag
    execution dag
    solution dag
        There are 2 *directed-acyclic-graphs* instances used:

        - the :attr:`.ExecutionPlan.dag`,  in the `execution plan`, which contains
          the `prune`\d  nodes, used to decide the `execution steps`;
        - the :attr:`.Solution.dag` in the `solution`, which derives the
          `canceled operation`\s due to `reschedule`\d/failed operations upstream.

    steps
    execution steps
        The `plan` contains a list of the operation-nodes only from the `dag`,
        topologically sorted, and interspersed with *instruction steps* needed to
        `compute` the asked `outputs` from the given `inputs`.

        They are built by :meth:`.Network._build_execution_steps()` based on
        the subgraph `dag`.

        The only *instruction* step other than an operation is for performing
        an `eviction`.

    eviction
        A memory footprint optimization where intermediate `inputs` & `outputs`
        are erased from `solution` as soon as they are not needed further down the `dag`.

        *Evictions* are pre-calculated during `planning`, denoted with the
        `dependency` inserted in the `steps` of the `execution plan`.

        `Evictions <eviction>` inhibit `overwrite`\s.

    inputs
        The named input values that are fed into an `operation` (or `pipeline`)
        through :meth:`.Operation.compute()` method according to its `needs`.

        These values are either:

        - given by the user to the outer `pipeline`, at the start of a `computation`, or
        - derived from `solution` using *needs* as keys, during intermediate `execution`.

    outputs
        The dictionary of computed values returned by an `operation` (or a `pipeline`)
        matching its `provides`, when method :meth:`.Operation.compute()` is called.

        Those values are either:

        - retained in the `solution`, internally during `execution`, keyed by
          the respective *provide*, or
        - returned to user after the outer *pipeline* has finished `computation`.

        When no specific outputs requested from a *pipeline*, :meth:`.Pipeline.compute()`
        returns all intermediate `inputs` along with the *outputs*, that is,
        no `eviction`\s happens.

        An *operation* may return `partial outputs`.

    pipeline
        The :class:`.Pipeline` `compose`\s and `compute`\s a `network`  of `operation`\s  against given `inputs` & `outputs`.

        This class is also an *operation*, so it specifies `needs` & `provides`
        but these are not *fixed*, in the sense that :meth:`.Pipeline.compute()`
        can potentially consume and provide different subsets of inputs/outputs.

    operation
        Either the abstract notion of an action with specified `needs` and `provides`,
        *dependencies*, or the concrete wrapper :class:`.FnOp` for
        (any :func:`callable`), that feeds on `inputs` and update `outputs`,
        from/to `solution`, or given-by/returned-to the user by a `pipeline`.

        The distinction between *needs*/*provides* and *inputs*/*outputs* is akin to
        function *parameters* and *arguments* during define-time and run-time,
        respectively.

    dependency
        The (possibly `hierarchical <subdoc>`) name of a `solution` value an `operation` `needs` or `provides`.

        - *Dependencies* are declared during `composition`, when building
          :class:`.FnOp` instances.
          *Operations* are then interlinked together, by matching the *needs* & *provides*
          of all *operations* contained in a `pipeline`.

        - During `planning` the `graph` is then `prune`\d based on the :term:`reachability
          <unsatisfied operation>` of the *dependencies*.

        - During `execution` :meth:`.Operation.compute()` performs 2 "matchings":

          - *inputs* & *outputs* in *solution* are accessed by the *needs* & *provides*
            names of the *operations*;
          - operation *needs* & *provides* are zipped against the underlying function's
            arguments and results.

          These matchings are affected by `modifier`\s, print-out with `diacritic`\s.

        .. include:: ../../graphtik/fnop.py
            :start-after: .. dep-attributes-start
            :end-before: .. dep-attributes-end

    needs
    fn_needs
    matching inputs
        The list of `dependency` names an `operation` requires from `solution` as `inputs`,

        roughly corresponding to underlying function's arguments (**fn_needs**).

        Specifically, :meth:`.Operation.compute()` extracts input values
        from *solution* by these names, and matches them against function arguments,
        mostly by their positional order.
        Whenever this matching is not 1-to-1, and function-arguments  differ from
        the regular *needs*, `modifier`\s must be used.

    provides
    user_provides
    fn_provides
    zipping outputs
        The list of `dependency` names an `operation` writes to the `solution` as `outputs`,

        roughly corresponding to underlying function's results (**fn_provides**).

        Specifically, :meth:`.Operation.compute()` "zips" this list-of-names
        with the `output <outputs>` values produced when the `operation`'s
        function is called.
        You may alter this "zipping" by one of the following methods:

        - artificially extended the *provides* with `alias`\ed *fn_provides*,
        - use `modifier`\s to annotate certain names with :func:`.keyword`, `sideffects`
          and/or `implicit`, or
        - mark the *operation* that its function `returns dictionary`, and
          cancel zipping.

        .. include:: ../../graphtik/fnop.py
            :start-after: .. provides-note-start
            :end-before: .. provides-note-end


    alias
        Map an existing name in `fn_provides` into a duplicate, artificial one in `provides` .

        You cannot alias an *alias*.  See :ref:`aliases`

    conveyor operation
    default identity function
        The default function if none given to an `operation` that conveys `needs` to `provides`.

        For this to happen when :meth:`.FnOp.compute()` is called,
        an operation *name* must have been given AND the number of `provides` must match
        that of the number of `needs`.

        :seealso: :ref:`conveyor-function` & :func:`.identity_function()`.

    returns dictionary
        When an `operation` is marked with :attr:`FnOp.returns_dict` flag,
        the underlying function is not expected to return `fn_provides` as a sequence
        but as a dictionary; hence, no "zipping" of function-results --> `fn_provides`
        takes place.

        Usefull for operations returning `partial outputs` to have full control
        over which `outputs` were actually produced, or to cancel `sideffects`.

    modifier
    diacritic
        A `modifier` change `dependency` behavior during `planning` or `execution`.

        For instance, a `needs` may be annotated as :func:`.keyword` and/or `optionals`
        function arguments, `provides` and *needs* can be annotated as "ghost" `sideffects`
        or assigned an `accessor` to work with `hierarchical data`.

        .. include:: ../../graphtik/modifier.py
            :start-after: .. diacritics-start
            :end-before: .. diacritics-end

        See :mod:`graphtik.modifier` module.

    optionals
        A `needs` only `modifier` for a `inputs` that do not hinder `operation` execution
        (`prune`) if absent from `solution`.

        In the underlying function it corresponds to either:

        - non-compulsory function arguments (with defaults), annotated with
          :func:`.optional`, or
        - `varargish` arguments, annotated with :func:`.vararg` or :func:`.varargs`.

    varargish
        A `needs` only `modifier` for `inputs` to be appended as ``*args``
        (if present in `solution`).

        There are 2 kinds, both, by definition, `optionals`:

        - the :func:`.vararg` annotates any *solution* value to be appended *once*
          in the ``*args``;
        - the :func:`.varargs` annotates *iterable* values and all its items are appended
          in the ``*args`` one-by-one.

        .. include:: ../../graphtik/modifier.py
            :start-after: .. varargs-mistake-start
            :end-before: .. varargs-mistake-end

        In printouts, it is denoted either with ``*`` or ``+`` `diacritic`.

        See also the elaborate example in :ref:`hierarchical-data` section.

    implicit
        A `modifier` denoting a `dependency` not fed into/out of the function,
        but the *dependency* is still considered while `planning`,
        expected to exist in the `solution`, downstream.

        One use case is for an operation to consume/produce a `subdoc`\(s)
        with its own means (not through `jsonp` `accessor`\s).

        Only a :func:`.modify` & :func:`.sfxed` *modifier* functions accept
        the ``implicit`` param.

        If an *implicit* cannot solve your problems, try `sideffects`...

    sideffects
        A `modifier` denoting a fictive `dependency` linking `operation`\s into virtual flows,
        without real data exchanges.

        The side-effect modification may happen to some internal state
        not fully represented in the `graph` & `solution`.

        There are actually 2 relevant *modifiers*:

        - An *abstract sideffect* modifier (annotated with :func:`.sfx`)
          describing modifications taking place beyond the scope of the solution.
          It may have just the "optional" `diacritic` in printouts.

          .. tip::
              Probably you either need `implicit`, or the next variant, not this one.

        - The `sideffected` modifier (annotated with :func:`.sfxed`)
          denoting modifications on a *real* dependency read from and written to
          the solution.

        Both kinds of sideffects participate in the `planning` of the graph,
        and both may be given or asked in the `inputs` & `outputs` of a `pipeline`,
        but they are never given to functions.
        A function of a `returns dictionary` operation can return a falsy value
        to declare it as `canceled <partial outputs>`.

    sideffected
    sfx_list
        A `modifier` denoting `sideffects`\(*sfx_list*) acting on a `solution` `dependency`,

        .. Note::will
            To be precise, the *"sideffected dependency"* is the name held in
            :attr:`._Modifier._sideffected` attribute of a *modifier* created by
            :func:`.sfxed()` function;  it may have all `diacritic`\s in printouts.

        The main use case is to declare an `operation` that both `needs` and `provides`
        the same *dependency*, to mutate it.
        When designing a `network` with many *sfxed* modifiers all based on
        the same *sideffected* dependency (i.e. with different `sfx_list`), then
        these should form a strict (no forks) sequence, or else, fork modifications
        will be lost.

        The `outputs` of a *sideffected dependency* will produce an `overwrite` if
        the *sideffected dependency* is declared both as *needs* and *provides*
        of some operation.

        See also the elaborate example in :ref:`hierarchical-data` section.

    accessor
        Getter/setter functions to extract/populate `solution` values given as a `modifier` parameter
        (not applicable for pure `sideffects`).

        See :class:`.Accessor` defining class and the :func:`.modify` concrete factory.

    subdoc
    superdoc
    doc chain
    data tree
    hierarchical data
        A **subdoc** is a `dependency` value nested further into another one
        (the **superdoc**),
        accessed with a `json pointer path` expression with respect to the `solution`,
        denoted with slashes like: ``root/parent/child/leaf``

        Whenever a nested dependency is given/asked, then all **docs-in-chain**
        (depicted below) are *topologically sorted*, before executing any operations
        working on them.

        .. graphviz::
            :caption:
                The **docs-in-chain** for a hypothetical dependency ``stats/b/b1``:
                **superdocs** at the *left*, **subdocs** at the *right* of ``b1``,
                respectively.

            digraph {
                rankdir=LR;
                node [color="grey80" fontcolor="grey80" label="..."]
                edge [color="grey80"]

                stats -> a -> {a1, a2}
                stats -> b -> b1 -> {b11, b12, b13}  [color="#8B4513"]
                b13 -> b131                          [color="#8B4513"]
                stats -> c -> c1

                stats [label=<stats> color="#8B4513" fontcolor="#8B4513" fillcolor="#E0E0E0" style=filled]
                b [label=<b> color="#8B4513" fontcolor="#8B4513" fillcolor="#E0E0E0" style=filled]
                b1 [label=<<B>b1</B>> color="#8B4513" fontcolor="#8B4513" penwidth=3 fillcolor="#E0E0E0" style=filled]
                b11 [label="b11" color="#8B4513" fontcolor="#8B4513"]
                b12 [label="b12" color="#8B4513" fontcolor="#8B4513"]
                b13 [label="b13" color="#8B4513" fontcolor="#8B4513"]
                b131 [label="b131" color="#8B4513" fontcolor="#8B4513"]
            }

        Note that if the root has been asked in `outputs`, none of its subdocs
        will be `evicted <eviction>`.

        :seealso: ::ref:`hierarchical-data` (example)

    json pointer path
    jsonp
        A `dependency` containing slashes(``/``) & `accessor`\s that can
        read and write `subdoc` values with `json pointer <https://tools.ietf.org/html/rfc6901>`_
        expressions, like ``root/parent/child/1/item``, resolved from `solution`.

        In addition to writing values, the :func:`.vcat` or :func:`.hcat` modifiers
        (& respective accessors) support also `pandas concatenation` for `provides`.

        Note that all non-root dependencies are implicitly created as jsonp
        if the operation has a `current-working-document` defined.

    cwd
    current-working-document
        A `jsonp` prefix of an `operation` (or `pipeline`) to prefix any non-root `dependency` defined.

    pandas concatenation
        A `jsonp` `dependency` in `provides` may `designate <modifier>` its respective
        :class:`~pandas.DataFrame` and/or :class:`~pandas.Series` `output value <outputs>`
        to be concatenated with existing Pandas objects in the `solution`
        (usefull for when working with :ref:`Pandas advanced indexing <pandas:advanced.hierarchical>`.
        or else, `sideffected`\s are needed to break read-update cycles on dataframes).

        See example in :ref:`jsnop-df-concat`.

    reschedule
    rescheduling
    partial outputs
    canceled operation
        The partial `pruning` of the `solution`'s dag during `execution`.
        It happens when any of these 2 conditions apply:

        - an `operation` is marked with the :attr:`.FnOp.rescheduled`
          attribute, which means that its underlying *callable* may produce
          only a subset of its `provides` (*partial outputs*);
        - `endurance` is enabled, either globally (in the `configurations`), or
          for a specific *operation*.

        The *solution* must then *reschedule* the remaining operations downstream,
        and possibly *cancel* some of those ( assigned in :attr:`.Solution.canceled`).

        *Partial operations* are usually declared with `returns dictionary` so that
        the underlying function can control which of the outputs are returned.

        See :ref:`rescheduled`

    endurance
    endured
        Keep executing as many `operation`\s as possible, even if some of them fail.
        Endurance for an operation  is enabled if :func:`.set_endure_operations()`
        is true globally in the `configurations` or if :attr:`.FnOp.endured`
        is true.

        You may interrogate :attr:`.Solution.executed` to discover the status
        of each executed operations or call one of :meth:`.check_if_incomplete()`
        or :meth:`.scream_if_incomplete()`.

        See :ref:`endured`

    predicate
    node predicate
        A callable(op, node-data) that should return true for nodes to be
        included in `graph` during `planning`.

    abort run
        A global `configurations` flag that when set with :func:`.abort_run()` function,
        it halts the execution of all currently or future `plan`\s.

        It is reset automatically on every call of :meth:`.Pipeline.compute()`
        (after a successful intermediate :term:`planning`), or manually,
        by calling :func:`.reset_abort()`.

    parallel
    parallel execution
    execution pool
    task
        .. attention::
            Deprecated, in favor of always producing a list of "parallelizable batches",
            to hook with other executors (e.g. *Dask*, Apache's *airflow*, *Celery*).
            *In the future*, just the single-process implementation will be kept,
            and `marshalling` should be handled externally.

        `execute` `operation`\s *in parallel*, with a `thread pool` or `process pool`
        (instead of `sequential`).
        Operations and `pipeline` are marked as such on construction, or enabled globally
        from `configurations`.

        Note a `sideffects` are not expected to function with *process pools*,
        certainly not when `marshalling` is enabled.

    process pool
        When the :class:`multiprocessing.pool.Pool` class is used for (deprecated) `parallel` execution,
        the `task`\s  must be communicated to/from the worker process, which requires
        `pickling <https://docs.python.org/library/pickle.html>`_, and that may fail.
        With pickling failures you may try `marshalling` with *dill* library,
        and see if that helps.

        Note that `sideffects` are not expected to function at all.
        certainly not when `marshalling` is enabled.

    thread pool
        When the :func:`multiprocessing.dummy.Pool` class is used for (deprecated) `parallel` execution,
        the `task`\s are run *in process*, so no `marshalling` is needed.

    marshalling
        (deprecated) Pickling `parallel` `operation`\s and their `inputs`/`outputs` using
        the :mod:`dill` module. It is `configured <configurations>` either globally
        with :func:`.set_marshal_tasks()` or set with a flag on each
        operation / `pipeline`.

        Note that `sideffects` do not work when this is enabled.

    plottable
        Objects that can plot their graph network, such as those inheriting :class:`.Plottable`,
        (:class:`.FnOp`, :class:`.Pipeline`, :class:`.Network`,
        :class:`.ExecutionPlan`, :class:`.Solution`) or a |pydot.Dot|_ instance
        (the result of the :meth:`.Plottable.plot()` method).

        Such objects may render as SVG in *Jupiter notebooks* (through their ``plot()`` method)
        and can render in a Sphinx site with with the :rst:dir:`graphtik` *RsT directive*.
        You may control the rendered image as explained in the *tip*  of
        the :ref:`plotting` section.

        SVGs are in rendered with the `zoom-and-pan javascript library
        <https://github.com/ariutta/svg-pan-zoom>`_

        .. include:: plotting.rst
            :start-after: .. serve-sphinx-warn-start
            :end-before: .. serve-sphinx-warn-end

    plotter
    plotting
        A :class:`.Plotter` is responsible for rendering `plottable`\s as images.
        It is the `active plotter` that does that, unless overridden in a
        :meth:`.Plottable.plot()` call.
        Plotters can be customized by :ref:`various means <plot-customizations>`,
        such `plot theme`.

    active plotter
    default active plotter
        The `plotter` currently installed "in-context" of the respective `graphtik
        configuration` - this term implies also any :ref:`plot-customizations`
        done on the active plotter (such as `plot theme`).

        Installation happens by calling one of :func:`.active_plotter_plugged()` or
        :func:`.set_active_plotter` functions.

        The **default** *active plotter* is the plotter instance that this project
        comes pre-configured with, ie, when no *plot-customizations* have yet happened.

        .. include:: ../../graphtik/plot.py
            :start-after: .. theme-warn-start
            :end-before: .. theme-warn-end

    plot theme
    current theme
        The mergeable and `expandable styles <style>` contained in a :class:`.plot.Theme` instance.

        The **current theme in-use** is the :attr:`.Plotter.default_theme` attribute of
        the `active plotter`, unless overridden with the :obj:`theme` parameter when
        calling :meth:`.Plottable.plot()` (conveyed internally as the value of the
        :attr:`.PlotArgs.theme` attribute).

    style
    style expansion
        A *style* is an attribute of a `plot theme`, either a scalar value or a dictionary.

        *Styles* are collected in :class:`stacks <.StylesStack>` and are :meth:`merged
        <.StylesStack.merge>` into a single dictionary after performing the following
        :meth:`expansions <.StylesStack.expand>`:

        .. include:: ../../graphtik/plot.py
            :start-after: .. theme-expansions-start
            :end-before: .. theme-expansions-end

        .. tip::
            if :ref:`debug` is enabled, the provenance of all style values
            appears in the tooltips of plotted graphs.

    configurations
    graphtik configuration
        The functions controlling `compile` & `execution` globally  are defined
        in :mod:`.config` module and +1 in :mod:`graphtik.plot` module;
        the underlying global data are stored in :class:`contextvars.ContextVar` instances,
        to allow for nested control.

        All *boolean* configuration flags are **tri-state** (``None, False, True``),
        allowing to "force" all operations, when they are not set to the ``None``
        value.  All of them default to ``None`` (false).

    callbacks
        x2 optional callables called before/after each `operation` :meth:`.Pipeline.compute()`.
        Attention, any errors will abort the pipeline execution.

        pre-op-callback
            Called from solution code before :term:`marshalling`.
            A use case would be to validate `solution`, or
            :ref:`trigger a breakpoint by some condition <break_with_pre_callback>`.

        post-op-callback:
            Called after solution have been populated with `operation` results.
            A use case would be to validate operation `outputs` and/or
            solution after results have been populated.

        Callbacks must have this signature::

            callbacks(op_cb) -> None

        ... where ``op_cb`` is an instance of the :class:`.OpTask`.

    jetsam
        When a pipeline or an operation fails, the original exception gets annotated
        with salvaged values from ``locals()`` and raised intact, and optionally
        (if :ref:`debug`) the diagram of the failed `plottable` is saved in temporary file.

        See :ref:`jetsam`.

.. default-role:: obj
.. |usage-overview| image:: images/GraphkitUsageOverview.svg
    :alt: Usage overview of graphtik library
    :width: 640px
    :align: middle
.. |v440-flowchart| raw:: html
    :file: images/GraphtikFlowchart-v4.4.0.svg
