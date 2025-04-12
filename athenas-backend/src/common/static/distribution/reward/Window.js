Ext._define('common.distribution.reward.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.distribution.reward.Restful',

    _resetRewardMatch: function(rewardId) {
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'refazendo a concorrência..' });

        mask.show();
        this.factoryRestful().resetMatch(
            rewardId,
            {
                scope: this,
                fn: function() { this.getMatchGrid().getStore().reload(); }
            },
            {
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Preparando concorrência',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {fn: function() { mask.hide(); }}
        );
    },

    resetRewardMatch: function() {

        Ext.Msg.show({
            title: 'Preparando concorrência',
            msg: 'Tem certeza que deseja refazer a concorrência para este objeto?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function(btn) {
                if (btn === 'yes') {
                    this._resetRewardMatch(this.objectId());
                }
            }
        });
    },

    getResetMatchButton: function (cfg) {
        if (!this._resetMatchButton) {
            this._resetMatchButton = Ext._create('Ext.Button', {
                text: 'Preparar Sorteio',
                scope: this,
                width: 100,
                handler: function() { this.resetRewardMatch() }
            });
        }
        return this._resetMatchButton;
    },

    getDistributeButton: function(cfg) {
        if(!this._distributeButton) {
            this._distributeButton = Ext._create('Ext.Button', {
                text: 'Sortear',
                scope: this,
                handler: function() {
                    var btn = this._distributeButton;
                    var self = this;
                    var mask = new Ext.LoadMask(this.getEl(), {msg: 'sorteando...'});

                    btn.disable();
                    Ext.Msg.show({
                        title: 'Distribuindo objeto',
                        msg: 'Tem certeza que deseja distribuir este objeto?',
                        icon: Ext.Msg.QUESTION,
                        buttons: Ext.Msg.YESNO,
                        scope: this,
                        fn: function(btn) {
                            if (btn === 'no') return;

                            mask.show();
                            this.factoryRestful().distribute(
                                [this.objectId()],
                                {
                                    scope: this,
                                    fn: function() {
                                        console.log('-> OK');
                                    }
                                },
                                {
                                    fn: function(message) {
                                        console.log('-> ERR {%s}', message);
                                        Ext.Msg.show({
                                            title: 'Distribuindo objeto',
                                            msg: message,
                                            icon: Ext.Msg.ERROR,
                                            buttons: Ext.Msg.OK
                                        });
                                    }
                                },
                                {
                                    fn: function() {
                                        self.objectIdObserve();
                                        mask.hide();
                                    }
                                }
                            );
                        }
                    });
                }
            });
        }

        return this._distributeButton;
    },

    getButtons: function(cfg) {
        if (!this._buttons) {
            var buttons = [
                this.getResetMatchButton(cfg),
                this.getDistributeButton(cfg),
                '->'
            ];

            buttons = buttons.concat(common.distribution.reward.Window.superclass.getButtons.call(this, cfg));

            this._buttons = buttons;
        }
        return this._buttons;
    },

    getMatchGrid: function (cfg) {
        if (!this._matchGrid) {
            this._matchGrid = Ext._create('common.distribution.match.Grid', {
                height: 300,
                disabled: true,
                stripeRows: true,
                gridAutoLoad: false
            });
        }
        return this._matchGrid;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 100,
                labelAlign: 'right',
                items: [
                    {
                        xtype: "textfield",
                        name: "title",
                        fieldLabel: "Título",
                        maxLength: 100,
                        anchor: '99%',
                        allowBlank: false
                    },
                    {
                        xtype: "textfield",
                        name: "external_number",
                        fieldLabel: "Número Externo",
                        maxLength: 100,
                        anchor: '99%',
                        allowBlank: true
                    },
                    {
                        xtype: 'panel',
                        title: 'Participantes disponíveis para este Objeto',
                        border: true,
                        style: {
                            marginTop: '10px'
                        },
                        items: [
                            this.getMatchGrid(cfg)
                        ]
                    }
                ]
            });

        return this._formPanel;
    },

    objectId: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._objectId = value;

            if(dispatch)
                this.objectIdObserve();
        }

        return this._objectId;
    },

    objectIdObserve: function() {
        this.oId = this.objectId();

        if(this.oId) {
            this.getMatchGrid().setParam('reward', this.oId);
            this.getMatchGrid().setFilterProperty('reward', this.oId, 100);
            this.getMatchGrid().enable();
            //this.getMatchGrid().getStore().reload();

            this.getDistributeButton().enable();
        }
        else {
            this.getMatchGrid().setParam('reward', 0);
            this.getMatchGrid().setFilterProperty('reward', 0, 100, false);
            this.getMatchGrid().getStore().removeAll();
            this.getMatchGrid().disable();

            this.getDistributeButton().disable();
        }
    },

    saveAndContinueCallback: function (instance) {
        this.objectId(instance.pk);
        this.action = 'update';

        if (!this.params.distribution) {
            Ext.Msg.show({
                title: 'Preparando sorteio',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Não foi possível recuperar o código da Distribuição.'
            });
            return;
        }
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            width: 500,
            autoHeight: true,
            buttonAlign: 'left',
            buttons: this.getButtons(cfg),
            saveAndContinue: {
                scope: this,
                fn: this.saveAndContinueCallback
            }
        });

        common.distribution.match.Window.superclass.constructor.call(this, cfg);
        this.objectId(this.oId);
    }
});
