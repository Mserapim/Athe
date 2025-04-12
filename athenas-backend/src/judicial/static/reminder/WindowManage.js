Ext._define('judicial.reminder.WindowManage', {
    extend: 'Ext.Window',

    width: 1200,
    height: 650,

    gridClass: 'judicial.reminder.Grid',

    getReminderGrid: function(cfg) {
        if(!this._grid) {
            this._grid = Ext._create(this.gridClass, {
                region: 'north',
                gridAutoLoad: false,
                height: 250,
                minHeight: 250,
                split: true,
                hideColumns: ['modified_by', 'modified_at'],
                hideActions: ['remove', 'edit', 'copy'],
                allowRemove: false,
                allowUpdate: false,
            });

            this._grid.getSelectionModel().on({
                scope: this,
                selectionchange: function (sm) {
                    var selection = sm.getSelections();

                    if (selection.length > 0)
                        this.reminder(selection[0].get('pk'));
                    else
                        this.reminder(null);
                }
            });

            this._grid.on({
                scope: this,
                deactivatedItem: function() {
                    console.log('mark dirty [deactivated]');
                    this.dirty = true;
                },
                createdItemGrid: function() {
                    console.log('mark dirty [created]');
                    this.dirty = true;
                 },
                updatedItemGrid: function() {
                    console.log('mark dirty [updated]');
                    this.dirty = true;
                },
                removedItemGrid: function() {
                    console.log('mark dirty [removed]');
                    this.dirty = true;
                }
            })
        }

        return this._grid;
    },

    reminder: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._reminder = value;

            if(dispatch)
                this.reminderObserve();
        }

        return this._reminder;
    },

    reminderObserve: function() {
        var reminder = this.reminder();
        this.getTilePanel().setPageContent('');
        tile = this.getTilePanel();

        if(reminder) {
            var rest = Ext._create('judicial.reminder.Restful');
            var mask = new Ext.LoadMask(tile.getEl(), {msg: 'carregando lembrete...'});

            mask.show();
            rest.rendered(
                reminder,
                {
                    scope: this,
                    fn: function(rst) {
                        if(rst.success) {
                            tile.setPageContent(rst.rendered);
                            (rst.extra_pages || []).forEach(
                                function(page) {
                                    tile.addPageContent(page);
                                }
                            );
                        }else {
                            tile.setPageContent('');
                            Ext.Msg.show({
                                title: 'Carregando documento',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    }
                },
                {
                    scope: this,
                    fn: function() {
                        tile.setPageContent('');
                        Ext.Msg.show({
                            title: 'Carregando documento',
                            msg: 'Recurso indisponivel no momento.',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                },
                {
                    fn: function() { mask.hide() }
                }
            );
        }
    },

    getTilePanel: function(cfg) {
        if(!this._tilePanel)
            this._tilePanel = Ext._create('core.TilePagePanel', {
                region: 'center',
                split: true,
                minHeight: 200,
                papperModel: 'card',
                flex: 1
            });

        return this._tilePanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, { title: 'Lembretes' });

        Ext.apply(
            cfg,
            {
                dirty: false,
                layout: 'border',
                items: [
                    this.getReminderGrid(cfg),
                    this.getTilePanel()
                ]
            }
        );

        judicial.reminder.WindowManage.superclass.constructor.call(this, cfg);
    }
});
