Ext._define('judicial.search.person.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getPersonGrid: function () {
        if (!this._gridPerson) {
            this._gridPerson = Ext._create('rh.person.Grid', {
                region: 'north',
                hideActions: ['edit', 'remove', 'copy'],
                allowUpdate: false,
                doubleClickHandler: function () { },
                hideItemsToolbar: ['person', '-', 'edit', 'remove', 'convert', 'merge', 'download'],
                height: 400,
                split: true,
                border: false,
            });

            this._gridPerson.getSelectionModel().on({
                scope: this,
                rowselect: function (sm, index, data) {
                    this.person(data.get('pk'));
                }
            });
        }

        return this._gridPerson;
    },

    person: function (value, prevent) {
        prevent = core.nullValue(prevent, false);

        if (value !== undefined) {
            this._person = value;

            !prevent && this.observePerson();
        }

        return this._person;
    },

    observePerson: function () {
        var value = this.person();

        if (value) {
            this.getLawsuitGrid().enable();
            this.getLawsuitGrid().setFilter([
                { property: 'has_interested__person', value: value, stage: 1000 },
                { property: 'blokes__commonperson__bloke', value: value, stage: 1000 },
                { property: 'blokes__person__bloke', value: value, stage: 1000 },
                { property: 'blokes__association__bloke', value: value, stage: 1000 },
                { property: 'blokes__company__bloke', value: value, stage: 1000 },
                { property: 'blokes__governmentpublic__bloke', value: value, stage: 1000 }
            ]);
        }
        else {
            this.getLawsuitGrid().disable();
            this.setFilter([], false);
            this.getLawsuitGrid().getStore().removeAll();
        }
    },

    getLawsuitGrid: function () {
        if (!this._gridLawsuit)
            this._gridLawsuit = Ext._create('judicial.search.person.Grid', {
                region: 'center',
                hideActions: ['copy', 'edit', 'remove'],
                hideItemsToolbar: ['openDocument', '-', 'introduction', 'followDeadline', 'protocolImport', 'bookmarker', 'download'],
                split: true,
                border: false,
                disabled: true,
                gridAutoLoad: false
            });

        return this._gridLawsuit;
    },

    constructor: function (cfg) {
        cfg = cfg ? cfg : {};

        Ext.apply(
            cfg,
            {
                title: 'Pesquisa Procedimentos',
                border: false,
                split: true,
                layout: 'border',
                items: [
                    this.getPersonGrid(),
                    this.getLawsuitGrid()
                ]
            }
        );

        judicial.search.person.Manage.superclass.constructor.call(this, cfg);
    }
});
