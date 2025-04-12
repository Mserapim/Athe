Ext._define('common.distribution.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'common.distribution.Window',

    configOrderToolBar: [
        'add',
        'edit',
        'remove',
        '-',
        'copyPlayers',
        '-',
        'report',
        '->',
        'download'
    ],

    _copyPlayers: function (params) {
        var OPERATION = 'Copiando participantes';

        var mask = new Ext.LoadMask(
            this.getEl(),
            {msg: OPERATION + '...'}
        );
        mask.show();

        this.factoryRestful().copyPlayers(
            params,
            {
                scope: this,
                fn: function (result) {
                    core.invokeCallback(this.afterCopyingPlayersCallback || {fn: Ext.emptyFn});
                }
            },
            {
                fn: function (error) {
                    Ext.Msg.show({
                        title: OPERATION,
                        msg: error,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                fn: function () {
                    mask.hide();
                }
            }
        );
    },

    _showSelectDistributionWindow: function () {
        var win = Ext._create(
            'common.distribution.SelectDistributionWindow',
            {
                closable: false
            }
        );

        win.show();

        win.on({
            scope: this,
            destroy: function (win) {
                this.srcDistribution(win.result);

                var title = 'Copiar participantes';
                var msg = [
                    'Esta ação copiará os participantes da distribuição de "origem"',
                    'para a distribuição de "destino". Tem certeza de que deseja',
                    'prosseguir?'
                ].join(' ');

                function confirmCallback(btn) {
                    if (btn === 'yes') {
                        this._copyPlayers({
                            src_distribution: this.srcDistribution(),
                            dst_distribution: this.dstDistribution()
                        });
                    }
                }

                if (this.dstDistribution()) {
                    if (this.srcDistribution()) {
                        Ext.MessageBox.confirm(
                            title,
                            msg,
                            confirmCallback,
                            this
                        );
                    }
                }
            }
        });
    },

    // get e set para distribuição de destino.
    dstDistribution: function (newValue) {
        if (newValue !== undefined && newValue !== this._dstDistribution) {
            this._dstDistribution = newValue;
        }

        return this._dstDistribution;
    },

    // get e set para distribuição de origem.
    srcDistribution: function (newValue) {
        if (newValue !== undefined && newValue !== this._srcDistribution) {
            this._srcDistribution = newValue;
        }

        return this._srcDistribution;
    },

    _copyPlayersMsgBoxConfirm: function () {
        var selections = this.getSelectionModel().getSelections();

        if (selections == 0) {
            Ext.Msg.show({
                title: 'Copiar participantes',
                msg: [
                    'Por favor, primeiramente selecione a Distribuição de "destino".',
                    "Em seguida clique novamente no botão Copiar Participantes."
                ].join(' '),
                icon: Ext.Msg.INFO,
                buttons: Ext.Msg.OK
            });

            return false;
        }

        Ext.MessageBox.confirm(
            'Copiar participantes',
            [
                'A Distribuição de "destino" é aquela que vai receber os Participantes.',
                'Você selecionou "', selections[0].data.title, '" como Distribuição de destino.',
                'Clique em "Sim" para continuar, ou em "Não" para selecionar outra Distribuição.'
            ].join(' '),
            function (btn) {
                if (btn === 'yes') {
                    this.dstDistribution(selections[0].data.pk);
                    this._showSelectDistributionWindow();
                }
            },
            this
        );

        // this.dstDistribution(selections[0].data.pk);
        // return true;
    },

    getCopyPlayersAction: function () {
        if (!this._copyPlayersAction) {
            this._copyPlayersAction = Ext._create('Ext.Button', {
                text: 'Copiar Participantes',
                tooltip: 'Copia os participantes de uma distribuição para outra.',
                iconCls: 'icon-16px icon-core icon-core-copy',
                scope: this,
                handler: function (btn, event) {
                    // if (this._copyPlayersMsgBoxConfirm()) {
                    //     this._showSelectDistributionWindow();
                    // }
                    this._copyPlayersMsgBoxConfirm();
                }
            });
        }
        return this._copyPlayersAction;
    },

    getReportAction: function () {
        if (!this._reportAction) {
            this._reportAction = Ext._create('Ext.Button', {
                text: 'Relatório',
                tooltip: 'Emite um relatório quantitativo de distribuição por servidor.',
                iconCls: 'icon-core icon-core-reports',
                scope: this,
                handler: function (btn, event) {
                    var selections = this.getSelectionModel().getSelections();

                    Ext._create('common.distribution.reports.DistributionByEmployee', {
                        pkset: selections.map(function (selection) {
                            return selection.data.pk;
                        }).join(',')
                    }).show();
                }
            });
        }
        return this._reportAction;
    },

    getColumnModel: function () {
        if (!this._columnModel) {

            var dateRenderer = Ext.util.Format.dateRenderer('d/m/Y H:i');

            this._columnModel = Ext._create('Ext.grid.ColumnModel', [
                Ext._create('Ext.grid.RowNumberer'),
                { header: 'Cod.', dataIndex: 'pk', hidden: true, width: 50, hidden: true },
                { header: 'Descrição', dataIndex: 'unicode', hidden: true },
                { header: 'Título', dataIndex: 'title', id: 'autoExpandColumn' },
                { header: 'Origem', dataIndex: 'origin_unicode', width: 350 },
                { header: 'Modificado em', dataIndex: 'modified_at', renderer: dateRenderer, width: 150, hidden: true },
                { header: 'Modificado por', dataIndex: 'modified_by_unicode', width: 150, hidden: true },
                { header: 'Criado em', dataIndex: 'created_at', renderer: dateRenderer, width: 150, hidden: true },
                { header: 'Criado por', dataIndex: 'created_by_unicode', width: 150 }
            ]);
        }

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'common.distribution.Restful',
    'common.distribution.Grid'
);
