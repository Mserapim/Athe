Ext._define('rh.workplacemigrate.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.workplacemigrate.Window',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'performMigration', '-', 'search', '->', 'download'],

    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'Tipo', dataIndex: 'type_of_migrate_display', id: 'autoExpandColumn' },
                    { header: 'Lotação', dataIndex: 'workplace_unicode', width: 240, sortable: true, hidden: false },
                    { header: 'Lotação destino', dataIndex: 'workplace_destiny_unicode', width: 240, sortable: true, hidden: false },
                    { header: 'Publicação', dataIndex: 'publication_unicode', width: 120, sortable: true, hidden: false },
                    { header: 'Executado por', dataIndex: 'signed_by_unicode', width: 120, sortable: true, hidden: false },
                    { header: 'Executado em', dataIndex: 'signed_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), sortable: false, hidden: true },
                    { header: 'Criado por', dataIndex: 'created_by_unicode', width: 120, sortable: true, hidden: true },
                    { header: 'Criado em', dataIndex: 'created_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), sortable: true, hidden: true },
                    { header: 'Modificado por', dataIndex: 'modified_by_unicode', width: 120, sortable: true, hidden: true },
                    { header: 'Modificado em', dataIndex: 'modified_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), sortable: true, hidden: true }
                ]
            );

        return this._columnModel;
    },

    getPerformMigrationAction: function () {
        if (!this._performMigrationButton) {
            this._performMigrationButton = Ext._create('Ext.Button', {
                text: 'Executar',
                qtip: 'Habilita para Procedimentos Extrajudiciais',
                iconCls: 'icon-core icon-core-run',
                scope: this,
                handler: this.performMigrationRunner,
            });
        }
        return this._performMigrationButton;
    },

    performMigrationRunner: function () {
        var selections = this.getSelectionModel().getSelections();

        if (selections.length > 0) {
            Ext.Msg.show({
                title: 'Executar migração',
                msg: 'Deseja executar a migração?', // CANCEL, ERROR, INFO, OK, OKCANCEL, QUESTION, WARNING, YESNO, YESNOCANCEL
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.OKCANCEL,
                scope: this,
                fn: function (btn) {
                    if (btn == 'cancel')
                        return;
                    else {
                        var pkset = selections.map(
                            function (item) {
                                return item.id;
                            }
                        );

                        var rest = this.factoryRestful();
                        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Processando...' });
                        mask.show();

                        rest.performMigration(
                            pkset,
                            {
                                scope: this,
                                fn: function (message) {
                                    this.responseMessage(Ext.Msg.INFO, message);
                                    this.getStore().reload();
                                }
                            },
                            {
                                scope: this,
                                fn: function (message) {
                                    this.responseMessage(Ext.Msg.ERROR, message);
                                }
                            },
                            {
                                scope: this,
                                fn: function () {
                                    mask.hide();
                                }
                            }
                        );
                    }
                }
            });
        } else {
            Ext.Msg.show({
                title: 'this.title',
                icon: Ext.Msg.WARNING,
                buttons: Ext.Msg.OK,
                msg: 'Selecione ao menos um registro'
            });
        }
    },
});

core.RestfulGrid.register(
    'rh.workplacemigrate.Restful',
    'rh.workplacemigrate.Grid'
);

