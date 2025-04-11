Ext._define('common.distribution.Manage', {
    extend: 'toolkit.widget.TabPanel',

    _MSG_COULD_NOT_APPLY_FILTER: 'Não foi possível aplicar o filtro. Por favor, selecione uma distribuição e tente novamente.',

    notifyDistributionObservers: function (data) {
        this.getDistributionObservers().forEach(function (observer) {
            observer.update(data);
        });
    },

    getDistributionObservers: function (cfg) {
        if (!this._observers) {
            this._observers = [];

            this._observers.push({
                scope: this,
                update: function (data) {
                    var playerGrid = this.scope.getPlayerGrid();
                    var selected = data.sm.getSelected();

                    if (selected) {
                        value = selected.get('pk');
                        playerGrid.enable();
                        playerGrid.setParam('distribution', value);
                        playerGrid.setFilterProperty('distribution', value, 100, false);
                        playerGrid.setFilterProperty('active', true, 200);
                    } else {
                        playerGrid.disable();
                        playerGrid.getStore().removeAll();
                    }
                }
            });

            this._observers.push({
                scope: this,
                update: function (data) {
                    var rewardGrid = this.scope.getRewardGrid();
                    var selected = data.sm.getSelected();

                    if (selected) {
                        value = selected.get('pk');
                        rewardGrid.enable();
                        rewardGrid.setParam('distribution', value);
                        rewardGrid.removeFilterProperty('winner__isnull', 1001, false);
                        rewardGrid.removeFilterProperty('canceled_at__isnull', 1002, false);
                        rewardGrid.removeFilterProperty('distributed_at__gte', 1003, false);
                        rewardGrid.removeFilterProperty('distributed_at__lte', 1004, false);
                        rewardGrid.removeFilterProperty('winner', 1005, false);
                        rewardGrid.setFilterProperty('distribution', value, 1000);
                    } else {
                        rewardGrid.disable();
                        rewardGrid.getStore().removeAll();
                    }
                }
            });

            this._observers.push({
                scope: this,
                update: function () {
                    var playerGrid = this.scope.getPlayerGrid();
                    playerGrid.getOnlyActiveMenuCheckItem().setChecked(true);
                }
            });
        }
        return this._observers;
    },

    player: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._player = value;

            if(dispatch)
                this.playerObserve();
        }

        return this._player;
    },

    playerObserve: function() {
        this.getRewardGrid().player(this.player());
    },

    getRewardGrid: function (cfg) {
        if(!this._rewardGrid) {
            this._rewardGrid = Ext._create('common.distribution.reward.Grid', {
                title: 'Objetos',
                region: 'center',
                width: '55%',
                gridAutoLoad: false,
            });
        }
        return this._rewardGrid;
    },

    getPlayerGrid: function (cfg) {
        if (!this._playerGrid) {
            this._playerGrid = Ext._create('common.distribution.player.Grid', {
                title: 'Participantes',
                region: 'west',
                width: '45%',
                minSize: 350,
                gridAutoLoad: false,
            });

            this._playerGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sm) {
                    var selection = sm.getSelections();

                    if (selection.length > 0)
                        this.player(selection[0].get('pk'));
                    else
                        this.player(null);
                }
            });
        }
        return this._playerGrid;
    },

    getDistributionGrid: function (cfg) {
        if (!this._distributionGrid) {
            this._distributionGrid = Ext._create('common.distribution.Grid', {
                title: 'Distribuições',
                region: 'north',
                height: 200,
                minHeight: 200,
                afterCopyingPlayersCallback: {
                    scope: this,
                    fn: function() {
                        this.getPlayerGrid().getStore().reload();
                    }
                }
            });

            this._distributionGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function (selectionModel) {
                    this.notifyDistributionObservers({sm: selectionModel});
                }
            });
        }
        return this._distributionGrid;
    },

    getCurrentPkOf: function (grid) {
        var selections = grid.getSelectionModel().getSelections();

        if (selections.length)
            return selections[0].data.pk;

        return 0;
    },

    _doRequest: function (action, params) {
        var PROCESSING_MSG = 'Realizando distribuição'
        var restful = this.getRewardGrid().factoryRestful();

        var mask = new Ext.LoadMask(
            this.getRewardGrid().getEl(),
            {msg: PROCESSING_MSG + '...'}
        );
        mask.show();

        restful.doRequest(
            restful.getRoute(action, false, 'POST', {
                params: params,
                scope: this,
                callback: function() {
                    mask.hide();
                    mask = null;
                },
                success: function(request) {
                    var result = Ext.decode(request.responseText);

                    if (result.successful) {
                        console.info(PROCESSING_MSG + ': ' + result.message);
                    } else {
                        Ext.Msg.show({
                            title: PROCESSING_MSG,
                            icon: 'ext-mb-' + result.msg_type,
                            buttons: Ext.Msg.OK,
                            msg: result.message
                        });
                    }
                },
                failure: function(request) {
                    Ext.Msg.show({
                        title: PROCESSING_MSG,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Funcionalidade indisponível no momento.'
                    });
                }
            })
        );
    },

    init: function () {
        this.getPlayerGrid().disable();
        this.getRewardGrid().disable();
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            layout: 'border',
            title: 'Gestor de Distribuição',
            defaults: {
                split: true,
                stripeRows: true
            },
            items: [
                this.getDistributionGrid(cfg),
                this.getPlayerGrid(cfg),
                this.getRewardGrid(cfg)
            ]
        });

        common.distribution.Manage.superclass.constructor.call(this, cfg);

        this.init();
    }
});
