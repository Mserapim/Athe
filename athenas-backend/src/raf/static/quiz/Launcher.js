Ext._define('raf.quiz.Launcher', {
    extend: 'toolkit.widget.TabPanel',

    getQuizGrid: function(cfg) {
        if (!this._quizGrid) {
            this._quizGrid = Ext._create('raf.quiz.Grid', {
                region: 'north',
                columnAction: false,
                gridAutoLoad: false,
                height: 300,
            });

            this._quizGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(selm) {
                    if (selm.getSelections().length > 0)
                        this.quiz(selm.getSelections()[0].get('pk'));
                    else
                        this.quiz(null);
                }
            });

            this._quizGrid.setFilterProperty('activated', 'true', 100);
        }
        return this._quizGrid;
    },

    getItemGrid: function(cfg) {
        if (!this._itemGrid) {
            this._itemGrid = Ext._create('raf.item.Grid', {
                title: 'Assuntos',
                margins: '0 2 0 0',
                region: 'center',
                flex: 1,
                layout: 'fit',
                columnAction: false,
                gridAutoLoad: false,
                hideColumns: ['quiz_unicode'],
            });
        }

        return this._itemGrid;
    },

    getSubItemGrid: function(cfg) {
        if (!this._subitemGrid)
            this._subitemGrid = Ext._create('raf.subitem.Grid', {
                title: 'Movimentos',
                margins: '0 0 0 2',
                region: 'south',
                flex: 1,
                layout: 'fit',
                columnAction: false,
                gridAutoLoad: false,
                hideColumns: ['quiz_unicode'],
            });

        return this._subitemGrid;
    },

    quiz: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if (value !== undefined) {
            this._quiz = value;

            if (dispatch)
                this.observerQuiz();
        }

        return this._quiz;
    },

    observerQuiz: function() {
        var value = this.quiz();

        if (value) {
            this.getItemGrid().enable();
            this.getItemGrid().setParam('quiz', value);
            this.getItemGrid().setFilterProperty('quiz', value, 100);

            this.getSubItemGrid().enable();
            this.getSubItemGrid().setParam('quiz', value);
            this.getSubItemGrid().setFilterProperty('quiz', value, 100);
        } else {
            this.getItemGrid().disable();
            this.getItemGrid().setParam('quiz', 0);
            this.getItemGrid().setFilterProperty('quiz', 0, 100, false);
            this.getItemGrid().getStore().removeAll();

            this.getSubItemGrid().disable();
            this.getSubItemGrid().setParam('quiz', 0);
            this.getSubItemGrid().setFilterProperty('quiz', 0, 100, false);
            this.getSubItemGrid().getStore().removeAll();
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Questionários'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getQuizGrid(cfg),
                    {

                        layout: {
                            type: 'hbox',
                            align: 'stretch'
                        },
                        region: 'center',
                        border: false,
                        items: [
                            this.getItemGrid(cfg),
                            this.getSubItemGrid(cfg)
                        ]
                    }
                ]
            }
        );

        raf.quiz.Launcher.superclass.constructor.call(this, cfg);

        this.quiz(cfg.oId === undefined ? null : cfg.oId);
    }
});
